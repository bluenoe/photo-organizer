#!/usr/bin/env python3
"""
Advanced Face Recognition Photo Organizer (GPU Accelerated Version)

This tool scans images in a folder, detects unique human faces using face_recognition,
and organizes photos by creating person-specific folders. Each image can be copied
to multiple folders if it contains multiple known people.

This version adds an option to use the CNN model for GPU-based face detection,
which is more accurate and significantly faster on a CUDA-enabled GPU.

Author: AI Assistant (Modified by Gemini for GPU support)
Version: 2.1
Requirements: face_recognition (with dlib compiled for CUDA), Pillow, numpy, tkinter
"""

import os
import sys
import json
import shutil
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

# Try to import required libraries
try:
    import face_recognition
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Error: face_recognition library not installed.")
    print("Install with: pip install face_recognition")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Face preview will be disabled.")


# TUI THÊM Ở ĐÂY: Hàm kiểm tra GPU
def is_gpu_available():
    """Check if dlib is compiled with CUDA support."""
    try:
        # face_recognition is built on dlib
        import dlib
        return dlib.DLIB_USE_CUDA and dlib.cuda.get_num_devices() > 0
    except (ImportError, AttributeError):
        return False

class FaceEncodingCache:
    """Manages face encoding cache for faster repeated runs"""
    
    def __init__(self, cache_file: str = "face_encodings_cache.pkl"):
        self.cache_file = cache_file
        self.cache: Dict[str, List[np.ndarray]] = {}
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
    
    def get_encodings(self, image_path: str) -> Optional[List[np.ndarray]]:
        """Get cached encodings for an image"""
        try:
            mtime = os.path.getmtime(image_path)
            cache_key = f"{image_path}_{mtime}"
            return self.cache.get(cache_key)
        except OSError:
            return None
    
    def set_encodings(self, image_path: str, encodings: List[np.ndarray]) -> None:
        """Cache encodings for an image"""
        try:
            mtime = os.path.getmtime(image_path)
            cache_key = f"{image_path}_{mtime}"
            self.cache[cache_key] = encodings
        except OSError:
            pass


class FaceData:
    """Represents a detected face with its encoding and metadata"""
    
    def __init__(self, encoding: np.ndarray, image_path: str, location: Tuple[int, int, int, int]):
        self.encoding = encoding
        self.image_path = image_path
        self.location = location  # (top, right, bottom, left)
        self.person_name: Optional[str] = None
    
    def get_face_image(self) -> Optional[Image.Image]:
        """Extract and return the face image"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            image = Image.open(self.image_path)
            top, right, bottom, left = self.location
            face_image = image.crop((left, top, right, bottom))
            return face_image
        except Exception as e:
            logging.error(f"Failed to extract face from {self.image_path}: {e}")
            return None


class FaceRecognitionOrganizer:
    """Main class for organizing photos by face recognition"""
    
    def __init__(self):
        self.setup_logging()
        self.cache = FaceEncodingCache()
        self.known_faces: Dict[str, np.ndarray] = {}  # person_name -> face_encoding
        self.unknown_faces: List[FaceData] = []
        self.image_extensions = {'.jpg', '.jpeg', '.png'}
        self.face_tolerance = 0.6
        self.use_gpu = False # TUI THÊM Ở ĐÂY
        
        # GUI components
        self.root = None
        self.progress_var = None
        self.status_var = None
    
    def setup_logging(self) -> None:
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('face_organizer.log'),
                logging.StreamHandler()
            ]
        )
    
    def find_image_files(self, folder_path: str) -> List[str]:
        """Find all supported image files in the folder"""
        image_files = []
        folder = Path(folder_path)
        
        for file_path in folder.rglob('*'):
            if file_path.suffix.lower() in self.image_extensions:
                image_files.append(str(file_path))
        
        logging.info(f"Found {len(image_files)} image files")
        return image_files
    
    # TUI SỬA Ở ĐÂY: Cập nhật hàm để dùng GPU
    def extract_face_encodings(self, image_path: str) -> List[FaceData]:
        """Extract face encodings from an image, using GPU if enabled."""
        cached_encodings = self.cache.get_encodings(image_path)
        if cached_encodings is not None:
            return [FaceData(enc, image_path, (0, 0, 0, 0)) for enc in cached_encodings]
        
        try:
            image = face_recognition.load_image_file(image_path)
            
            # Chọn model dựa trên tùy chọn của người dùng
            model_to_use = "cnn" if self.use_gpu else "hog"
            logging.info(f"Using face detection model: {model_to_use}")
            
            face_locations = face_recognition.face_locations(image, model=model_to_use)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            self.cache.set_encodings(image_path, face_encodings)
            
            face_data_list = []
            for encoding, location in zip(face_encodings, face_locations):
                face_data_list.append(FaceData(encoding, image_path, location))
            
            return face_data_list
            
        except Exception as e:
            logging.error(f"Failed to process {image_path}: {e}")
            return []
    
    def find_unique_faces(self, image_files: List[str]) -> List[FaceData]:
        """Find all unique faces across all images"""
        all_faces = []
        unique_faces = []
        
        # Extract faces from all images
        for i, image_path in enumerate(image_files):
            if self.progress_var:
                self.progress_var.set((i / len(image_files)) * 50)
                self.root.update_idletasks()
            
            if self.status_var:
                self.status_var.set(f"Processing {os.path.basename(image_path)}...")
            
            faces = self.extract_face_encodings(image_path)
            all_faces.extend(faces)
        
        logging.info(f"Extracted {len(all_faces)} faces from {len(image_files)} images")
        
        if not all_faces:
             return []

        # Group similar faces
        used_indices = set()
        
        known_encodings_list = [face.encoding for face in all_faces]

        for i, face in enumerate(all_faces):
            if i in used_indices:
                continue
            
            if self.progress_var:
                self.progress_var.set(50 + (i / len(all_faces)) * 50)
                self.root.update_idletasks()
            
            unique_faces.append(face)
            used_indices.add(i)

            # Compare this face to all others in a vectorized way
            distances = face_recognition.face_distance(known_encodings_list[i+1:], face.encoding)
            
            for j, distance in enumerate(distances):
                actual_index = i + 1 + j
                if actual_index in used_indices:
                    continue
                
                if distance <= self.face_tolerance:
                    used_indices.add(actual_index)
        
        logging.info(f"Found {len(unique_faces)} unique faces")
        return unique_faces
    
    def show_face_preview(self, face_data: FaceData) -> None:
        """Show a preview of the detected face"""
        if not PIL_AVAILABLE:
            return
        
        face_image = face_data.get_face_image()
        if face_image is None:
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Face Preview - {os.path.basename(face_data.image_path)}")
        preview_window.geometry("300x350")
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        # Resize face image for preview
        face_image = face_image.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(face_image)
        
        # Display image
        img_label = ttk.Label(preview_window, image=photo)
        img_label.image = photo  # Keep reference
        img_label.pack(pady=10)
        
        # Show source file info
        info_label = ttk.Label(preview_window, 
                              text=f"Found in: {os.path.basename(face_data.image_path)}",
                              font=("Arial", 10))
        info_label.pack(pady=5)
        
        # Close button
        ttk.Button(preview_window, text="Close", 
                  command=preview_window.destroy).pack(pady=10)
    
    def get_person_name(self, face_data: FaceData) -> Optional[str]:
        """Get person name for a face through GUI dialog"""
        if PIL_AVAILABLE:
            self.show_face_preview(face_data)
        
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
            if self.status_var:
                self.status_var.set(f"Naming face {i+1} of {len(unique_faces)}...")
            
            name = self.get_person_name(face)
            if name:
                face.person_name = name
                self.known_faces[name] = face.encoding
                logging.info(f"Named face as: {name}")
            else:
                logging.info("Skipped naming this face")
    
    def identify_person_in_image(self, image_path: str) -> Set[str]:
        """Identify all known people in an image"""
        people_found = set()
        
        if not self.known_faces:
             return people_found

        try:
            faces = self.extract_face_encodings(image_path)
            if not faces:
                return people_found

            known_names = list(self.known_faces.keys())
            known_encodings = list(self.known_faces.values())
            
            for face in faces:
                # Compare against all known faces at once
                matches = face_recognition.compare_faces(known_encodings, face.encoding, self.face_tolerance)
                
                # Find the first match
                for i, match in enumerate(matches):
                    if match:
                        people_found.add(known_names[i])
        
        except Exception as e:
            logging.error(f"Failed to identify people in {image_path}: {e}")
        
        return people_found
    
    def organize_photos(self, source_folder: str, destination_folder: str) -> None:
        """Organize photos by copying them to person-specific folders"""
        if not self.known_faces:
            messagebox.showwarning("No Named Faces", "No faces were named. Cannot organize photos.")
            return
        
        os.makedirs(destination_folder, exist_ok=True)
        
        image_files = self.find_image_files(source_folder)
        
        stats = defaultdict(int)
        organized_count = 0
        
        for i, image_path in enumerate(image_files):
            if self.progress_var:
                self.progress_var.set((i / len(image_files)) * 100)
                self.root.update_idletasks()
            
            if self.status_var:
                self.status_var.set(f"Organizing {os.path.basename(image_path)}...")
            
            people_in_image = self.identify_person_in_image(image_path)
            
            if people_in_image:
                if organized_count == 0 or (organized_count % len(people_in_image) == 0):
                     organized_count += 1

                for person_name in people_in_image:
                    person_folder = os.path.join(destination_folder, person_name)
                    os.makedirs(person_folder, exist_ok=True)
                    
                    filename = os.path.basename(image_path)
                    dest_path = os.path.join(person_folder, filename)
                    
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
        
        self.cache.save_cache()
        
        result_message = f"Organization complete!\n\n"
        result_message += f"Total images processed: {len(image_files)}\n"
        result_message += f"Images with recognized faces: {organized_count}\n\n"
        result_message += "Photos per person:\n"
        
        for person, count in stats.items():
            result_message += f"  {person}: {count} photos\n"
        
        messagebox.showinfo("Organization Complete", result_message)
        
        if self.status_var:
            self.status_var.set("Ready")
    
    # TUI SỬA Ở ĐÂY: Cập nhật giao diện
    def create_gui(self) -> None:
        """Create the main GUI interface"""
        self.root = tk.Tk()
        self.root.title("Face Recognition Photo Organizer (GPU Enabled)")
        self.root.geometry("600x550") # Tăng chiều cao
        
        self.source_folder_var = tk.StringVar()
        self.dest_folder_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        self.gpu_var = tk.BooleanVar(value=False) # Biến cho checkbox GPU
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Face Recognition Photo Organizer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Label(main_frame, text="Source Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_source_folder).grid(row=1, column=2, pady=5)
        
        ttk.Label(main_frame, text="Destination Folder:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dest_folder_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_dest_folder).grid(row=2, column=2, pady=5)
        
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Label(settings_frame, text="Face Recognition Tolerance:").grid(row=0, column=0, sticky=tk.W)
        tolerance_var = tk.DoubleVar(value=self.face_tolerance)
        tolerance_scale = ttk.Scale(settings_frame, from_=0.3, to=0.8, 
                                   variable=tolerance_var, orient=tk.HORIZONTAL)
        tolerance_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        ttk.Label(settings_frame, text="(Lower = More Strict)").grid(row=0, column=2, sticky=tk.W)
        
        def update_tolerance(val):
            self.face_tolerance = tolerance_var.get()
        
        tolerance_scale.configure(command=update_tolerance)
        
        # TUI THÊM Ở ĐÂY: Checkbox để bật GPU
        gpu_checkbox = ttk.Checkbutton(settings_frame, 
                                       text="Use GPU Acceleration (Requires NVIDIA GPU & correct setup)",
                                       variable=self.gpu_var,
                                       command=self.toggle_gpu)
        gpu_checkbox.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Vô hiệu hóa checkbox nếu không có GPU
        if not is_gpu_available():
            gpu_checkbox.config(state=tk.DISABLED)
            self.gpu_var.set(False)
            self.status_var.set("Ready (GPU not available or dlib not compiled with CUDA)")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Start Organization", 
                  command=self.start_organization).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Cache", 
                  command=self.clear_cache).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="Progress:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=580)
        status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(1, weight=1)
    
    # TUI THÊM Ở ĐÂY
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
            messagebox.showinfo("Cache Cleared", "Face encoding cache has been cleared.")
            logging.info("Face encoding cache cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {e}")
    
    def start_organization(self) -> None:
        """Start the photo organization process"""
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

        try:
            self.progress_var.set(0)
            self.status_var.set("Finding images...")
            self.root.update_idletasks()
            
            image_files = self.find_image_files(source_folder)
            if not image_files:
                messagebox.showwarning("No Images", "No supported image files found in the source folder.")
                self.status_var.set("Ready")
                return
            
            self.status_var.set("Analyzing faces... This may take a while.")
            self.root.update_idletasks()
            unique_faces = self.find_unique_faces(image_files)
            
            if not unique_faces:
                messagebox.showwarning("No Faces", "No faces were detected in the images.")
                self.status_var.set("Ready")
                return
            
            self.status_var.set("Waiting for user input...")
            self.assign_names_to_faces(unique_faces)
            
            self.status_var.set("Organizing photos...")
            self.organize_photos(source_folder, dest_folder)
            
        except Exception as e:
            logging.error(f"Organization failed: {e}", exc_info=True)
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.status_var.set("Error occurred. Check log for details.")
    
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
    organizer = FaceRecognitionOrganizer()
    organizer.run()


if __name__ == "__main__":
    main()