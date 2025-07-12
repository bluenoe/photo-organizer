#!/usr/bin/env python3
"""
Advanced Face Recognition Photo Organizer (GPU Accelerated & Optimized Version)

This tool scans images in a folder, detects unique human faces using face_recognition,
and organizes photos by creating person-specific folders. Each image can be copied
to multiple folders if it contains multiple known people.

This optimized version includes:
- Parallel processing with ThreadPoolExecutor
- Image resizing for faster face detection
- Improved face grouping algorithms
- Non-blocking UI with progress updates
- GPU acceleration with CNN model
- Enhanced caching system
- Memory optimization for large datasets

Author: AI Assistant (Optimized for Performance)
Version: 3.0
Requirements: face_recognition (with dlib compiled for CUDA), Pillow, numpy, tkinter
"""

import os
import sys
import json
import shutil
import logging
import pickle
import threading
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from queue import Queue

# Try to import required libraries
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

try:
    import numpy as np
except ImportError:
    import sys
    print("Error: numpy library not installed.")
    print("Install with: pip install numpy")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Face preview will be disabled.")


def is_gpu_available():
    """Check if dlib is compiled with CUDA support."""
    try:
        import dlib
        return dlib.DLIB_USE_CUDA and dlib.cuda.get_num_devices() > 0
    except (ImportError, AttributeError):
        return False


class ToolTip:
    """Create a tooltip for a given widget"""
    
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
    
    def enter(self, event=None):
        self.schedule()
    
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)  # 500ms delay
    
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def showtip(self, event=None):
        try:
            # Try to get bbox for text widgets
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
        except (tk.TclError, AttributeError):
            # For widgets without bbox method (like Labels), use widget position
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"), wraplength=300)
        label.pack(ipadx=1)
    
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class OptimizedFaceEncodingCache:
    """Enhanced face encoding cache with better performance and memory management"""
    
    def __init__(self, cache_file: str = "face_encodings_cache.pkl"):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict] = {}  # Enhanced cache structure
        self.memory_cache: Dict[str, List[np.ndarray]] = {}  # In-memory cache
        self.max_memory_items = 1000  # Limit memory cache size
        self.load_cache()
    
    def load_cache(self) -> None:
        """Load face encodings from cache file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                logging.info(f"Loaded {len(self.cache)} cached encodings")
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}")
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save face encodings to cache file"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            logging.info(f"Saved {len(self.cache)} encodings to cache")
        except Exception as e:
            logging.warning(f"Failed to save cache: {e}")
    
    def get_cache_key(self, image_path: str) -> str:
        """Generate cache key based on file path and modification time"""
        try:
            mtime = os.path.getmtime(image_path)
            file_size = os.path.getsize(image_path)
            return f"{image_path}_{mtime}_{file_size}"
        except OSError:
            return f"{image_path}_unknown"
    
    def get_encodings(self, image_path: str) -> Optional[List[np.ndarray]]:
        """Get cached encodings for an image"""
        cache_key = self.get_cache_key(image_path)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check disk cache
        if cache_key in self.cache:
            encodings = self.cache[cache_key].get('encodings')
            if encodings is not None:
                # Add to memory cache if space available
                if len(self.memory_cache) < self.max_memory_items:
                    self.memory_cache[cache_key] = encodings
                return encodings
        
        return None
    
    def set_encodings(self, image_path: str, encodings: List[np.ndarray], 
                     locations: List[Tuple[int, int, int, int]] = None) -> None:
        """Cache encodings for an image with metadata"""
        cache_key = self.get_cache_key(image_path)
        
        # Store in both memory and disk cache
        cache_data = {
            'encodings': encodings,
            'locations': locations or [],
            'timestamp': time.time()
        }
        
        self.cache[cache_key] = cache_data
        
        # Add to memory cache if space available
        if len(self.memory_cache) < self.max_memory_items:
            self.memory_cache[cache_key] = encodings
        
    def clear_old_entries(self, max_age_days: int = 30) -> None:
        """Remove old cache entries to prevent unlimited growth"""
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        keys_to_remove = []
        for key, data in self.cache.items():
            if isinstance(data, dict) and 'timestamp' in data:
                if current_time - data['timestamp'] > max_age_seconds:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
            if key in self.memory_cache:
                del self.memory_cache[key]
        
        if keys_to_remove:
            logging.info(f"Removed {len(keys_to_remove)} old cache entries")


class FaceData:
    """Represents a detected face with its encoding and metadata"""
    
    def __init__(self, encoding: np.ndarray, image_path: str, 
                 location: Tuple[int, int, int, int], confidence: float = 1.0):
        self.encoding = encoding
        self.image_path = image_path
        self.location = location  # (top, right, bottom, left)
        self.confidence = confidence
        self.person_name: Optional[str] = None
        self._face_image_cache: Optional[Image.Image] = None
    
    def get_face_image(self, size: Tuple[int, int] = (200, 200)) -> Optional[Image.Image]:
        """Extract and return the face image with caching"""
        if not PIL_AVAILABLE:
            return None
        
        if self._face_image_cache is not None:
            return self._face_image_cache.resize(size, Image.Resampling.LANCZOS)
        
        try:
            image = Image.open(self.image_path)
            top, right, bottom, left = self.location
            
            # Add padding around face
            padding = 20
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(image.width, right + padding)
            bottom = min(image.height, bottom + padding)
            
            face_image = image.crop((left, top, right, bottom))
            self._face_image_cache = face_image
            
            return face_image.resize(size, Image.Resampling.LANCZOS)
        except Exception as e:
            logging.error(f"Failed to extract face from {self.image_path}: {e}")
            return None


class OptimizedFaceRecognitionOrganizer:
    """Optimized main class for organizing photos by face recognition"""
    
    def __init__(self):
        
        self.cache = OptimizedFaceEncodingCache()
        self.setup_logging()
        self.known_faces: Dict[str, np.ndarray] = {}
        self.unknown_faces: List[FaceData] = []
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.face_tolerance = 0.6
        self.use_gpu = False
        
        # Performance settings
        self.max_workers = min(8, os.cpu_count() or 4)  # Limit thread count
        self.batch_size = 50  # Process images in batches
        self.resize_factor = 0.5  # Resize images for faster processing
        self.min_face_size = 50  # Minimum face size to detect
        
        # GUI components
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.processing_thread = None
        self.stop_processing = False
        
        # Progress tracking
        self.progress_queue = Queue()
        
    def setup_logging(self) -> None:
        """Configure logging with better formatting"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('face_organizer.log'),
                logging.StreamHandler()
            ]
        )
        
        # Clear old cache entries on startup
        self.cache.clear_old_entries()
    
    def find_image_files(self, folder_path: str) -> List[str]:
        """Find all supported image files in the folder with better filtering"""
        image_files = []
        folder = Path(folder_path)
        
        for file_path in folder.rglob('*'):
            if (file_path.suffix.lower() in self.image_extensions and 
                file_path.is_file() and file_path.stat().st_size > 1024):  # Skip tiny files
                image_files.append(str(file_path))
        
        # Sort by file size (smaller files first for faster initial processing)
        image_files.sort(key=lambda x: os.path.getsize(x))
        
        logging.info(f"Found {len(image_files)} image files")
        return image_files
    
    def resize_image_for_processing(self, image_path: str) -> Optional[np.ndarray]:
        """Load and resize image for faster face detection"""
        try:
            # Load image with PIL for better memory management
            pil_image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Resize for faster processing while maintaining aspect ratio
            original_size = pil_image.size
            new_size = (int(original_size[0] * self.resize_factor), 
                       int(original_size[1] * self.resize_factor))
            
            # Don't resize if image is already small
            if new_size[0] < 300 or new_size[1] < 300:
                resized_image = pil_image
            else:
                resized_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array for face_recognition
            return np.array(resized_image)
            
        except Exception as e:
            logging.error(f"Failed to load/resize image {image_path}: {e}")
            return None
    
    def extract_face_encodings_optimized(self, image_path: str) -> List[FaceData]:
        """Optimized face encoding extraction with caching and resizing"""
        # Check cache first
        cached_encodings = self.cache.get_encodings(image_path)
        if cached_encodings is not None:
            return [FaceData(enc, image_path, (0, 0, 0, 0)) for enc in cached_encodings]
        
        try:
            # Load and resize image
            image = self.resize_image_for_processing(image_path)
            if image is None:
                return []
            
            # Choose model based on GPU availability and user preference
            model_to_use = "cnn" if (self.use_gpu and is_gpu_available()) else "hog"
            
            # Detect faces with optimized parameters
            face_locations = face_recognition.face_locations(
                image, 
                model=model_to_use,
                number_of_times_to_upsample=1  # Reduce upsampling for speed
            )
            
            if not face_locations:
                self.cache.set_encodings(image_path, [])
                return []
            
            # Filter out very small faces
            filtered_locations = []
            for location in face_locations:
                top, right, bottom, left = location
                face_width = right - left
                face_height = bottom - top
                if face_width >= self.min_face_size and face_height >= self.min_face_size:
                    # Scale back to original image coordinates
                    if self.resize_factor != 1.0:
                        scale = 1.0 / self.resize_factor
                        location = (
                            int(top * scale),
                            int(right * scale),
                            int(bottom * scale),
                            int(left * scale)
                        )
                    filtered_locations.append(location)
            
            if not filtered_locations:
                self.cache.set_encodings(image_path, [])
                return []
            
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            # Cache the results
            self.cache.set_encodings(image_path, face_encodings, filtered_locations)
            
            # Create FaceData objects
            face_data_list = []
            for encoding, location in zip(face_encodings, filtered_locations):
                face_data_list.append(FaceData(encoding, image_path, location))
            
            return face_data_list
            
        except Exception as e:
            logging.error(f"Failed to process {image_path}: {e}")
            return []
    
    def process_image_batch(self, image_paths: List[str]) -> List[FaceData]:
        """Process a batch of images in parallel"""
        all_faces = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.extract_face_encodings_optimized, path): path 
                for path in image_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                if self.stop_processing:
                    break
                    
                path = future_to_path[future]
                try:
                    faces = future.result(timeout=30)  # 30 second timeout per image
                    all_faces.extend(faces)
                    
                    # Update progress
                    self.progress_queue.put(('progress', len(all_faces)))
                    self.progress_queue.put(('status', f"Processed {os.path.basename(path)}"))
                    
                except Exception as e:
                    logging.error(f"Failed to process {path}: {e}")
        
        return all_faces
    
    def find_unique_faces_optimized(self, image_files: List[str]) -> List[FaceData]:
        """Optimized face detection and grouping with parallel processing"""
        all_faces = []
        
        # Process images in batches
        total_batches = (len(image_files) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(total_batches):
            if self.stop_processing:
                break
                
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(image_files))
            batch_files = image_files[start_idx:end_idx]
            
            self.progress_queue.put(('status', f"Processing batch {batch_idx + 1}/{total_batches}"))
            
            # Process batch
            batch_faces = self.process_image_batch(batch_files)
            all_faces.extend(batch_faces)
            
            # Update progress
            progress = (batch_idx + 1) / total_batches * 50  # First 50% for face detection
            self.progress_queue.put(('progress_percent', progress))
        
        if not all_faces:
            return []
        
        logging.info(f"Extracted {len(all_faces)} faces from {len(image_files)} images")
        
        # Optimized face grouping using vectorized operations
        self.progress_queue.put(('status', "Grouping similar faces..."))
        unique_faces = self.group_similar_faces_optimized(all_faces)
        
        logging.info(f"Found {len(unique_faces)} unique faces")
        return unique_faces
    
    def group_similar_faces_optimized(self, all_faces: List[FaceData]) -> List[FaceData]:
        """Optimized face grouping using vectorized distance calculations"""
        if not all_faces:
            return []
        
        unique_faces = []
        used_indices = set()
        
        # Extract all encodings for vectorized processing
        all_encodings = np.array([face.encoding for face in all_faces])
        
        for i, face in enumerate(all_faces):
            if i in used_indices or self.stop_processing:
                continue
            
            unique_faces.append(face)
            used_indices.add(i)
            
            # Vectorized distance calculation for remaining faces
            remaining_indices = [j for j in range(i + 1, len(all_faces)) if j not in used_indices]
            
            if remaining_indices:
                remaining_encodings = all_encodings[remaining_indices]
                distances = face_recognition.face_distance(remaining_encodings, face.encoding)
                
                # Find matches
                matches = distances <= self.face_tolerance
                matched_indices = [remaining_indices[j] for j, match in enumerate(matches) if match]
                used_indices.update(matched_indices)
            
            # Update progress
            progress = 50 + (i / len(all_faces)) * 50  # Second 50% for grouping
            self.progress_queue.put(('progress_percent', progress))
        
        return unique_faces
    
    def show_face_preview_optimized(self, face_data: FaceData) -> None:
        """Optimized face preview with better image handling"""
        if not PIL_AVAILABLE:
            return
        
        face_image = face_data.get_face_image((250, 250))
        if face_image is None:
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Face Preview - {os.path.basename(face_data.image_path)}")
        preview_window.geometry("350x400")
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        # Center the window
        preview_window.update_idletasks()
        x = (preview_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (preview_window.winfo_screenheight() // 2) - (400 // 2)
        preview_window.geometry(f"350x400+{x}+{y}")
        
        # Display image
        photo = ImageTk.PhotoImage(face_image)
        img_label = ttk.Label(preview_window, image=photo)
        img_label.image = photo  # Keep reference
        img_label.pack(pady=10)
        
        # Show source file info
        info_text = f"Found in: {os.path.basename(face_data.image_path)}\nConfidence: {face_data.confidence:.2f}"
        info_label = ttk.Label(preview_window, text=info_text, font=("Arial", 10))
        info_label.pack(pady=5)
        
        # Close button
        ttk.Button(preview_window, text="Close", 
                  command=preview_window.destroy).pack(pady=10)
    
    def get_person_name(self, face_data: FaceData) -> Optional[str]:
        """Get person name for a face through GUI dialog"""
        if PIL_AVAILABLE:
            self.show_face_preview_optimized(face_data)
        
        name = simpledialog.askstring(
            "Name This Person",
            f"Please enter a name for this person\n(Found in: {os.path.basename(face_data.image_path)}):",
            parent=self.root
        )
        
        if name:
            name = name.strip().replace(' ', '_')
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                name = name.replace(char, '_')
        
        return name
    
    def assign_names_to_faces(self, unique_faces: List[FaceData]) -> None:
        """Assign names to unique faces through user interaction"""
        for i, face in enumerate(unique_faces):
            if self.stop_processing:
                break
                
            self.progress_queue.put(('status', f"Naming face {i+1} of {len(unique_faces)}..."))
            
            name = self.get_person_name(face)
            if name:
                face.person_name = name
                self.known_faces[name] = face.encoding
                logging.info(f"Named face as: {name}")
            else:
                logging.info("Skipped naming this face")
    
    def identify_person_in_image_optimized(self, image_path: str) -> Set[str]:
        """Optimized person identification in an image"""
        people_found = set()
        
        if not self.known_faces:
            return people_found
        
        try:
            faces = self.extract_face_encodings_optimized(image_path)
            if not faces:
                return people_found
            
            known_names = list(self.known_faces.keys())
            known_encodings = list(self.known_faces.values())
            
            # Vectorized comparison for all faces at once
            face_encodings = [face.encoding for face in faces]
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    known_encodings, face_encoding, self.face_tolerance
                )
                
                for i, match in enumerate(matches):
                    if match:
                        people_found.add(known_names[i])
                        break  # Only need first match per face
        
        except Exception as e:
            logging.error(f"Failed to identify people in {image_path}: {e}")
        
        return people_found
    
    def organize_photos_optimized(self, source_folder: str, destination_folder: str) -> None:
        """Optimized photo organization with parallel processing"""
        if not self.known_faces:
            messagebox.showwarning("No Named Faces", "No faces were named. Cannot organize photos.")
            return
        
        os.makedirs(destination_folder, exist_ok=True)
        image_files = self.find_image_files(source_folder)
        
        stats = defaultdict(int)
        organized_count = 0
        
        # Process in batches for better memory management
        batch_size = min(50, len(image_files))
        total_batches = (len(image_files) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            if self.stop_processing:
                break
                
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(image_files))
            batch_files = image_files[start_idx:end_idx]
            
            # Process batch
            for i, image_path in enumerate(batch_files):
                if self.stop_processing:
                    break
                    
                overall_progress = ((batch_idx * batch_size + i) / len(image_files)) * 100
                self.progress_queue.put(('progress_percent', overall_progress))
                self.progress_queue.put(('status', f"Organizing {os.path.basename(image_path)}..."))
                
                people_in_image = self.identify_person_in_image_optimized(image_path)
                
                if people_in_image:
                    organized_count += 1
                    
                    for person_name in people_in_image:
                        person_folder = os.path.join(destination_folder, person_name)
                        os.makedirs(person_folder, exist_ok=True)
                        
                        filename = os.path.basename(image_path)
                        dest_path = os.path.join(person_folder, filename)
                        
                        # Handle duplicates
                        counter = 1
                        base_name, ext = os.path.splitext(filename)
                        while os.path.exists(dest_path):
                            new_filename = f"{base_name}_{counter}{ext}"
                            dest_path = os.path.join(person_folder, new_filename)
                            counter += 1
                        
                        try:
                            shutil.copy2(image_path, dest_path)
                            stats[person_name] += 1
                            logging.info(f"Copied {filename} to {person_name} folder")
                        except Exception as e:
                            logging.error(f"Failed to copy {image_path} to {dest_path}: {e}")
        
        # Save cache
        self.cache.save_cache()
        
        # Show results
        result_message = f"Organization complete!\n\n"
        result_message += f"Total images processed: {len(image_files)}\n"
        result_message += f"Images with recognized faces: {organized_count}\n\n"
        result_message += "Photos per person:\n"
        
        for person, count in stats.items():
            result_message += f"  {person}: {count} photos\n"
        
        messagebox.showinfo("Organization Complete", result_message)
        self.progress_queue.put(('status', "Ready"))
    
    def update_progress(self):
        """Update GUI progress from background thread"""
        try:
            while True:
                try:
                    item = self.progress_queue.get_nowait()
                    if item[0] == 'progress_percent':
                        if self.progress_var:
                            self.progress_var.set(item[1])
                    elif item[0] == 'status':
                        if self.status_var:
                            self.status_var.set(item[1])
                    elif item[0] == 'done':
                        break
                except:
                    break
            
            if self.root:
                self.root.after(100, self.update_progress)
        except:
            pass
    
    def create_gui(self) -> None:
        """Create the enhanced GUI interface"""
        self.root = tk.Tk()
        self.root.title("Face Recognition Photo Organizer (GPU Enabled & Optimized)")
        self.root.geometry("700x650")
        
        self.source_folder_var = tk.StringVar()
        self.dest_folder_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        self.gpu_var = tk.BooleanVar(value=False)
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Face Recognition Photo Organizer (Optimized)", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder selection
        source_label = ttk.Label(main_frame, text="Source Folder:")
        source_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        ToolTip(source_label, "Select the folder containing photos to organize by faces")
        
        source_entry = ttk.Entry(main_frame, textvariable=self.source_folder_var, width=60)
        source_entry.grid(row=1, column=1, padx=5, pady=5)
        ToolTip(source_entry, "Path to the folder with photos you want to organize")
        
        source_browse = ttk.Button(main_frame, text="Browse", command=self.browse_source_folder)
        source_browse.grid(row=1, column=2, pady=5)
        ToolTip(source_browse, "Click to browse and select the source folder")
        
        dest_label = ttk.Label(main_frame, text="Destination Folder:")
        dest_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        ToolTip(dest_label, "Select where organized photos will be saved")
        
        dest_entry = ttk.Entry(main_frame, textvariable=self.dest_folder_var, width=60)
        dest_entry.grid(row=2, column=1, padx=5, pady=5)
        ToolTip(dest_entry, "Path where organized photos will be copied to person-specific folders")
        
        dest_browse = ttk.Button(main_frame, text="Browse", command=self.browse_dest_folder)
        dest_browse.grid(row=2, column=2, pady=5)
        ToolTip(dest_browse, "Click to browse and select the destination folder")
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Tolerance setting
        tolerance_label = ttk.Label(settings_frame, text="Face Recognition Tolerance:")
        tolerance_label.grid(row=0, column=0, sticky=tk.W)
        ToolTip(tolerance_label, "Controls how strict face matching is. Lower values = more strict matching, higher values = more lenient matching")
        
        tolerance_var = tk.DoubleVar(value=self.face_tolerance)
        tolerance_scale = ttk.Scale(settings_frame, from_=0.3, to=0.8, 
                                   variable=tolerance_var, orient=tk.HORIZONTAL)
        tolerance_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        ToolTip(tolerance_scale, "Drag to adjust face recognition sensitivity. 0.3 = very strict, 0.8 = very lenient")
        
        tolerance_hint = ttk.Label(settings_frame, text="(Lower = More Strict)")
        tolerance_hint.grid(row=0, column=2, sticky=tk.W)
        ToolTip(tolerance_hint, "Lower values reduce false matches but may miss some correct matches")
        
        def update_tolerance(val):
            self.face_tolerance = tolerance_var.get()
        tolerance_scale.configure(command=update_tolerance)
        
        # GPU setting
        gpu_checkbox = ttk.Checkbutton(settings_frame, 
                                       text="Use GPU Acceleration (Requires NVIDIA GPU & CUDA)",
                                       variable=self.gpu_var,
                                       command=self.toggle_gpu)
        gpu_checkbox.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        ToolTip(gpu_checkbox, "Enable GPU acceleration for faster face detection. Requires NVIDIA GPU with CUDA support and dlib compiled with CUDA")
        
        # Performance settings
        perf_frame = ttk.LabelFrame(settings_frame, text="Performance", padding="5")
        perf_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        ToolTip(perf_frame, "Adjust performance settings to optimize processing speed")
        
        threads_label = ttk.Label(perf_frame, text="Max Threads:")
        threads_label.grid(row=0, column=0, sticky=tk.W)
        ToolTip(threads_label, "Maximum number of threads to use for parallel face encoding")
        
        thread_var = tk.IntVar(value=self.max_workers)
        thread_spinbox = ttk.Spinbox(perf_frame, from_=1, to=16, textvariable=thread_var, width=10)
        thread_spinbox.grid(row=0, column=1, padx=5)
        ToolTip(thread_spinbox, "Set the number of parallel threads (1-16). More threads = faster processing but higher CPU usage")
        
        def update_threads():
            self.max_workers = thread_var.get()
        thread_spinbox.configure(command=update_threads)
        
        resize_label = ttk.Label(perf_frame, text="Resize Factor:")
        resize_label.grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ToolTip(resize_label, "Scale down image size before processing to improve speed")
        
        resize_var = tk.DoubleVar(value=self.resize_factor)
        resize_scale = ttk.Scale(perf_frame, from_=0.25, to=1.0, variable=resize_var, orient=tk.HORIZONTAL)
        resize_scale.grid(row=0, column=3, padx=5)
        ToolTip(resize_scale, "Lower values = smaller image size = faster processing. 0.25 = 4x smaller, 1.0 = original size")
        
        def update_resize(val):
            self.resize_factor = resize_var.get()
        resize_scale.configure(command=update_resize)
        
        # Disable GPU if not available
        if not is_gpu_available():
            gpu_checkbox.config(state=tk.DISABLED)
            self.gpu_var.set(False)
            self.status_var.set("Ready (GPU not available)")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Organization", 
                                      command=self.start_organization_threaded)
        self.start_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.start_button, "Begin the face recognition and photo organization process")
        
        self.stop_button = ttk.Button(button_frame, text="Stop Processing", 
                                     command=self.stop_organization, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.stop_button, "Stop the current processing operation")
        
        clear_button = ttk.Button(button_frame, text="Clear Cache", command=self.clear_cache)
        clear_button.pack(side=tk.LEFT, padx=5)
        ToolTip(clear_button, "Clear the face encoding cache to free up disk space or force re-processing")
        
        # Progress
        progress_label = ttk.Label(main_frame, text="Progress:")
        progress_label.grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        ToolTip(progress_label, "Shows the current processing progress")
        
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ToolTip(progress_bar, "Visual progress indicator showing completion percentage")
        
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=680)
        status_label.grid(row=7, column=0, columnspan=3, pady=5)
        ToolTip(status_label, "Current status and detailed information about the processing step")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        perf_frame.columnconfigure(1, weight=1)
        perf_frame.columnconfigure(3, weight=1)
        
        # Start progress updater
        self.update_progress()
    
    def toggle_gpu(self):
        """Update the use_gpu flag when checkbox is toggled."""
        self.use_gpu = self.gpu_var.get()
        if self.use_gpu:
            logging.info("GPU acceleration enabled by user.")
            messagebox.showinfo("GPU Mode Enabled", 
                                "GPU acceleration has been enabled.\n"
                                "Face detection will now use the 'cnn' model, which is more accurate.\n"
                                "The first run may be slow as the model is downloaded.")
        else:
            logging.info("GPU acceleration disabled by user.")
    
    def browse_source_folder(self) -> None:
        """Browse for source folder"""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder_var.set(folder)
    
    def browse_dest_folder(self) -> None:
        """Browse for destination folder"""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder_var.set(folder)
    
    def clear_cache(self) -> None:
        """Clear the face encoding cache"""
        try:
            if os.path.exists(self.cache.cache_file):
                os.remove(self.cache.cache_file)
            self.cache.cache = {}
            self.cache.memory_cache = {}
            messagebox.showinfo("Cache Cleared", "Face encoding cache has been cleared.")
            logging.info("Face encoding cache cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {e}")
    
    def stop_organization(self):
        """Stop the current processing"""
        self.stop_processing = True
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.progress_queue.put(('status', "Stopping..."))
    
    def start_organization_threaded(self) -> None:
        """Start the photo organization process in a separate thread"""
        source_folder = self.source_folder_var.get()
        dest_folder = self.dest_folder_var.get()
        
        if not source_folder or not dest_folder:
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return
        
        if not os.path.exists(source_folder):
            messagebox.showerror("Error", "Source folder does not exist.")
            return
        
        if self.use_gpu and not is_gpu_available():
            messagebox.showerror("GPU Error", "GPU mode is enabled, but a compatible GPU was not found.\n"
                                              "Please ensure you have an NVIDIA GPU and dlib is compiled with CUDA.")
            return
        
        # Reset state
        self.stop_processing = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self.start_organization_worker, 
                                                 args=(source_folder, dest_folder))
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def start_organization_worker(self, source_folder: str, dest_folder: str) -> None:
        """Worker function for photo organization"""
        try:
            self.progress_queue.put(('progress_percent', 0))
            self.progress_queue.put(('status', "Finding images..."))
            
            image_files = self.find_image_files(source_folder)
            if not image_files:
                messagebox.showwarning("No Images", "No supported image files found in the source folder.")
                self.progress_queue.put(('status', "Ready"))
                return
            
            self.progress_queue.put(('status', "Analyzing faces... This may take a while."))
            unique_faces = self.find_unique_faces_optimized(image_files)
            
            if not unique_faces:
                messagebox.showwarning("No Faces", "No faces were detected in the images.")
                self.progress_queue.put(('status', "Ready"))
                return
            
            if not self.stop_processing:
                self.progress_queue.put(('status', "Waiting for user input..."))
                # Switch back to main thread for GUI interaction
                self.root.after(0, lambda: self.assign_names_and_organize(unique_faces, source_folder, dest_folder))
            
        except Exception as e:
            logging.error(f"Organization failed: {e}", exc_info=True)
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.progress_queue.put(('status', "Error occurred. Check log for details."))
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def assign_names_and_organize(self, unique_faces: List[FaceData], source_folder: str, dest_folder: str):
        """Assign names and organize photos (runs in main thread for GUI)"""
        try:
            self.assign_names_to_faces(unique_faces)
            
            if not self.stop_processing:
                self.progress_queue.put(('status', "Organizing photos..."))
                # Run organization in background thread again
                org_thread = threading.Thread(target=self.organize_photos_optimized, 
                                             args=(source_folder, dest_folder))
                org_thread.daemon = True
                org_thread.start()
        except Exception as e:
            logging.error(f"Failed to assign names or organize: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def run(self) -> None:
        """Run the application"""
        if not FACE_RECOGNITION_AVAILABLE:
            messagebox.showerror("Missing Dependencies", 
                               "face_recognition library is required but not installed.\n\n"
                               "Install with: pip install face_recognition")
            return
        
        self.create_gui()
        self.root.mainloop()


def main():
    """Main entry point"""
    organizer = OptimizedFaceRecognitionOrganizer()
    organizer.run()


if __name__ == "__main__":
    main()