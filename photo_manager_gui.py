#!/usr/bin/env python3
"""
Photo Manager - A comprehensive GUI application for organizing and managing photo libraries

Features:
- Duplicate file detection and management with visual preview
- Name-based grouping (e.g., files with "Nayeon" in name go to Nayeon folder)
- Date-based organization using EXIF data or file modification date
- Modern GUI with tkinter/ttk

Author: AI Assistant
Version: 1.0
"""

import os
import shutil
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import datetime
from collections import defaultdict
import re
from pathlib import Path

# Try to import PIL for image processing and preview
try:
    from PIL import Image, ImageTk
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Image preview and EXIF data extraction will be disabled.")
    print("To install Pillow, run: pip install Pillow")

# Try to import face_recognition for face detection and recognition
try:
    import face_recognition
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition not installed. Face-based organization will be disabled.")
    print("To install face_recognition, run: pip install face_recognition")

class PhotoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Manager - Organize Your Photo Library")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.find_duplicates = tk.BooleanVar(value=True)
        self.group_by_name = tk.BooleanVar(value=True)
        
        # Data storage
        self.duplicate_groups = []
        self.files_to_process = []
        self.face_encodings = {}  # Store face encodings with names
        self.unknown_faces = []  # Store unknown face encodings with file paths
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Photo Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Source folder selection
        ttk.Label(main_frame, text="Source Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_folder, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.select_source_folder).grid(row=1, column=2, pady=5)
        
        # Destination folder selection
        ttk.Label(main_frame, text="Destination Folder:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dest_folder, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.select_dest_folder).grid(row=2, column=2, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Checkbutton(options_frame, text="Find & Manage Duplicates", variable=self.find_duplicates).grid(row=0, column=0, sticky=tk.W)
        
        # Add face recognition option
        self.group_by_face = tk.BooleanVar(value=False)
        face_checkbox = ttk.Checkbutton(options_frame, text="Group by Face Recognition", variable=self.group_by_face)
        face_checkbox.grid(row=1, column=0, sticky=tk.W)
        if not FACE_RECOGNITION_AVAILABLE:
            face_checkbox.config(state="disabled")
            
        ttk.Checkbutton(options_frame, text="Group by Similar Name", variable=self.group_by_name).grid(row=2, column=0, sticky=tk.W)
        
        # Action button
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(action_frame, text="Start Organizing", command=self.start_organizing, style="Accent.TButton")
        self.start_button.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status/Log area
        log_frame = ttk.LabelFrame(main_frame, text="Status & Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def log_message(self, message):
        """Add a message to the log area"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def select_source_folder(self):
        """Select source folder dialog"""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)
            
    def select_dest_folder(self):
        """Select destination folder dialog"""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder.set(folder)
            
    def get_image_files(self, folder):
        """Get all image files from the folder recursively"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
        image_files = []
        
        for root, dirs, files in os.walk(folder):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_files.append(os.path.join(root, file))
                    
        return image_files
        
    def calculate_file_hash(self, filepath):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.log_message(f"Error calculating hash for {filepath}: {str(e)}")
            return None
            
    def find_duplicate_files(self, files):
        """Find duplicate files based on content hash"""
        self.log_message("Scanning for duplicate files...")
        hash_to_files = defaultdict(list)
        
        for i, filepath in enumerate(files):
            if i % 10 == 0:  # Update progress every 10 files
                self.log_message(f"Processed {i}/{len(files)} files for duplicates")
                
            file_hash = self.calculate_file_hash(filepath)
            if file_hash:
                hash_to_files[file_hash].append(filepath)
                
        # Filter out single files (no duplicates)
        duplicate_groups = [group for group in hash_to_files.values() if len(group) > 1]
        
        self.log_message(f"Found {len(duplicate_groups)} groups of duplicate files")
        return duplicate_groups
        
    def extract_base_name(self, filename):
        """Extract base name from filename for grouping"""
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Common patterns to identify base names
        # Remove numbers, underscores, hyphens, and common suffixes
        patterns = [
            r'[_-]\d+$',  # Remove trailing numbers with separators
            r'\d+$',      # Remove trailing numbers
            r'[_-](copy|photo|pic|image|selfie|portrait)$',  # Remove common suffixes
            r'[_-]\d{4}$',  # Remove years
            r'[_-]\d{1,2}[_-]\d{1,2}$',  # Remove date patterns
        ]
        
        base_name = name_without_ext
        for pattern in patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
            
        # Clean up any remaining separators at the end
        base_name = base_name.rstrip('_-')
        
        # If the base name is too short or empty, use the original name
        if len(base_name) < 2:
            base_name = name_without_ext
            
        return base_name
        
    def get_image_date(self, filepath):
        """Get the date when the image was taken from EXIF data or file modification date"""
        try:
            # Try to get EXIF date first if PIL is available
            if PIL_AVAILABLE:
                with Image.open(filepath) as img:
                    exif_data = img._getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == "DateTime" or tag == "DateTimeOriginal":
                                try:
                                    return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                except ValueError:
                                    continue
        except Exception:
            pass
            
        # Fall back to file modification date
        try:
            timestamp = os.path.getmtime(filepath)
            return datetime.datetime.fromtimestamp(timestamp)
        except Exception:
            return datetime.datetime.now()
            
    def create_date_folder_structure(self, date_obj, base_dest):
        """Create and return the folder structure based on date"""
        year = str(date_obj.year)
        month = f"{date_obj.month:02d}-{date_obj.strftime('%B')}"
        
        folder_path = os.path.join(base_dest, year, month)
        os.makedirs(folder_path, exist_ok=True)
        
        return folder_path
        
    def get_unique_filename(self, dest_path, filename):
        """Get a unique filename if the file already exists"""
        if not os.path.exists(os.path.join(dest_path, filename)):
            return filename
            
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter}{ext}"
            if not os.path.exists(os.path.join(dest_path, new_filename)):
                return new_filename
            counter += 1
            
    def start_organizing(self):
        """Main function to start the organization process"""
        if not self.source_folder.get() or not self.dest_folder.get():
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return
            
        if not os.path.exists(self.source_folder.get()):
            messagebox.showerror("Error", "Source folder does not exist.")
            return
            
        # Create destination folder if it doesn't exist
        os.makedirs(self.dest_folder.get(), exist_ok=True)
        
        self.start_button.config(state="disabled")
        self.progress.start()
        
        try:
            # Get all image files
            self.log_message("Scanning for image files...")
            all_files = self.get_image_files(self.source_folder.get())
            self.log_message(f"Found {len(all_files)} image files")
            
            if not all_files:
                messagebox.showinfo("Info", "No image files found in the source folder.")
                return
                
            # Handle duplicates if enabled
            files_to_organize = all_files.copy()
            if self.find_duplicates.get():
                self.duplicate_groups = self.find_duplicate_files(all_files)
                if self.duplicate_groups:
                    self.show_duplicate_manager()
                    # Wait for duplicate manager to close
                    self.root.wait_window(self.duplicate_window)
                    # Update files list after duplicate handling
                    files_to_organize = [f for f in all_files if os.path.exists(f)]
            
            # Handle face recognition if enabled
            if self.group_by_face.get() and FACE_RECOGNITION_AVAILABLE:
                self.log_message("Starting face recognition analysis...")
                self.analyze_faces(files_to_organize)
                if self.unknown_faces:
                    self.show_face_naming_dialog()
                    # Wait for face naming dialog to close
                    self.root.wait_window(self.face_naming_window)
                    
            # Organize remaining files
            self.organize_files(files_to_organize)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.log_message(f"Error: {str(e)}")
        finally:
            self.progress.stop()
            self.start_button.config(state="normal")
            
    def organize_files(self, files):
        """Organize files by date and optionally by name"""
        self.log_message("Starting file organization...")
        
        organized_count = 0
        name_groups = defaultdict(list) if self.group_by_name.get() else None
        
        for i, filepath in enumerate(files):
            try:
                if i % 10 == 0:
                    self.log_message(f"Processing {i}/{len(files)} files")
                    
                # Get image date
                image_date = self.get_image_date(filepath)
                
                # Create date-based folder structure
                date_folder = self.create_date_folder_structure(image_date, self.dest_folder.get())
                
                filename = os.path.basename(filepath)
                
                # Handle face-based grouping first (higher priority)
                if self.group_by_face.get() and FACE_RECOGNITION_AVAILABLE:
                    person_name = self.get_person_name_for_image(filepath)
                    if person_name:
                        # Create subfolder for this person
                        person_folder = os.path.join(date_folder, person_name)
                        os.makedirs(person_folder, exist_ok=True)
                        dest_folder = person_folder
                    else:
                        dest_folder = date_folder
                # Handle name grouping if face recognition is not used
                elif self.group_by_name.get():
                    base_name = self.extract_base_name(filename)
                    if base_name and len(base_name) > 1:
                        # Create subfolder for this base name
                        name_folder = os.path.join(date_folder, base_name)
                        os.makedirs(name_folder, exist_ok=True)
                        dest_folder = name_folder
                    else:
                        dest_folder = date_folder
                else:
                    dest_folder = date_folder
                    
                # Get unique filename
                unique_filename = self.get_unique_filename(dest_folder, filename)
                dest_path = os.path.join(dest_folder, unique_filename)
                
                # Copy the file
                shutil.copy2(filepath, dest_path)
                organized_count += 1
                
            except Exception as e:
                self.log_message(f"Error processing {filepath}: {str(e)}")
                
        self.log_message(f"Organization complete! {organized_count} files organized.")
        messagebox.showinfo("Success", f"Organization complete!\n{organized_count} files have been organized.")
        
    def analyze_faces(self, image_files):
        """Analyze faces in all images and store encodings"""
        if not FACE_RECOGNITION_AVAILABLE:
            return
            
        self.unknown_faces = []
        total_files = len(image_files)
        
        for i, filepath in enumerate(image_files):
            try:
                self.progress_var.set((i / total_files) * 100)
                self.root.update_idletasks()
                
                # Load image and find faces
                image = face_recognition.load_image_file(filepath)
                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)
                
                if face_encodings:
                    # Store the first face encoding found in the image
                    self.unknown_faces.append({
                        'filepath': filepath,
                        'encoding': face_encodings[0],
                        'location': face_locations[0]
                    })
                    
            except Exception as e:
                self.log_message(f"Error analyzing {os.path.basename(filepath)}: {str(e)}")
                
        self.log_message(f"Found {len(self.unknown_faces)} images with faces")
    
    def get_person_name_for_image(self, filepath):
        """Get the person name for an image based on face recognition"""
        if not FACE_RECOGNITION_AVAILABLE or not self.face_encodings:
            return None
            
        try:
            # Load image and find faces
            image = face_recognition.load_image_file(filepath)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                return None
                
            # Compare with known faces
            for name, known_encoding in self.face_encodings.items():
                matches = face_recognition.compare_faces([known_encoding], face_encodings[0])
                if matches[0]:
                    return name
                    
        except Exception as e:
            self.log_message(f"Error recognizing face in {os.path.basename(filepath)}: {str(e)}")
            
        return None
    
    def show_face_naming_dialog(self):
        """Show dialog for naming unknown faces"""
        self.face_naming_window = tk.Toplevel(self.root)
        self.face_naming_window.title("Name the Faces")
        self.face_naming_window.geometry("600x500")
        self.face_naming_window.transient(self.root)
        self.face_naming_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.face_naming_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        ttk.Label(main_frame, text="Please name the faces found in your photos:", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Scrollable frame for faces
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Process unique faces
        unique_faces = self.get_unique_faces()
        self.face_name_entries = {}
        
        for i, face_data in enumerate(unique_faces):
            face_frame = ttk.LabelFrame(scrollable_frame, text=f"Face {i+1}")
            face_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Image preview
            try:
                if PIL_AVAILABLE:
                    image = Image.open(face_data['filepath'])
                    # Crop face from image
                    top, right, bottom, left = face_data['location']
                    face_image = image.crop((left, top, right, bottom))
                    face_image = face_image.resize((100, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(face_image)
                    
                    img_label = ttk.Label(face_frame, image=photo)
                    img_label.image = photo  # Keep a reference
                    img_label.pack(side=tk.LEFT, padx=5, pady=5)
            except Exception as e:
                ttk.Label(face_frame, text="Preview not available").pack(side=tk.LEFT, padx=5, pady=5)
            
            # Name entry
            name_frame = ttk.Frame(face_frame)
            name_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            ttk.Label(name_frame, text="Name:").pack(anchor=tk.W)
            name_entry = ttk.Entry(name_frame, width=20)
            name_entry.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Label(name_frame, text=f"Found in: {os.path.basename(face_data['filepath'])}", 
                     font=("Arial", 8)).pack(anchor=tk.W)
            
            self.face_name_entries[i] = {
                'entry': name_entry,
                'encoding': face_data['encoding'],
                'files': face_data['files']
            }
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Names", command=self.save_face_names).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Skip Face Recognition", command=self.skip_face_recognition).pack(side=tk.RIGHT)
    
    def get_unique_faces(self):
        """Group similar faces together and return unique faces"""
        if not self.unknown_faces:
            return []
            
        unique_faces = []
        used_indices = set()
        
        for i, face_data in enumerate(self.unknown_faces):
            if i in used_indices:
                continue
                
            # Find all similar faces
            similar_files = [face_data['filepath']]
            current_encoding = face_data['encoding']
            
            for j, other_face in enumerate(self.unknown_faces[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                # Compare faces
                matches = face_recognition.compare_faces([current_encoding], other_face['encoding'], tolerance=0.6)
                if matches[0]:
                    similar_files.append(other_face['filepath'])
                    used_indices.add(j)
            
            used_indices.add(i)
            unique_faces.append({
                'filepath': face_data['filepath'],
                'encoding': face_data['encoding'],
                'location': face_data['location'],
                'files': similar_files
            })
            
        return unique_faces
    
    def save_face_names(self):
        """Save the names assigned to faces"""
        for face_id, face_data in self.face_name_entries.items():
            name = face_data['entry'].get().strip()
            if name:
                # Store the face encoding with the name
                self.face_encodings[name] = face_data['encoding']
                self.log_message(f"Saved face: {name} ({len(face_data['files'])} photos)")
        
        self.face_naming_window.destroy()
    
    def skip_face_recognition(self):
        """Skip face recognition and close dialog"""
        self.face_naming_window.destroy()
    
    def show_duplicate_manager(self):
        """Show duplicate file management window"""
        self.duplicate_window = tk.Toplevel(self.root)
        self.duplicate_window.title("Duplicate File Manager")
        self.duplicate_window.geometry("800x600")
        self.duplicate_window.transient(self.root)
        self.duplicate_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.duplicate_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Duplicate File Manager", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Create three-panel layout
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Groups list
        left_frame = ttk.LabelFrame(paned_window, text="Duplicate Groups", padding="5")
        paned_window.add(left_frame, weight=1)
        
        self.groups_listbox = tk.Listbox(left_frame)
        groups_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.groups_listbox.yview)
        self.groups_listbox.configure(yscrollcommand=groups_scrollbar.set)
        self.groups_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        groups_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate groups list
        for i, group in enumerate(self.duplicate_groups):
            self.groups_listbox.insert(tk.END, f"Group {i+1}: {len(group)} files")
            
        self.groups_listbox.bind('<<ListboxSelect>>', self.on_group_select)
        
        # Center panel - Files and preview
        center_frame = ttk.LabelFrame(paned_window, text="Files & Preview", padding="5")
        paned_window.add(center_frame, weight=2)
        
        # Files list
        files_frame = ttk.Frame(center_frame)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(files_frame, text="Files in selected group:").pack(anchor=tk.W)
        
        self.files_listbox = tk.Listbox(files_frame, height=6)
        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Preview area
        preview_frame = ttk.LabelFrame(center_frame, text="Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.preview_label = ttk.Label(preview_frame, text="Select a file to preview")
        self.preview_label.pack(expand=True)
        
        # Right panel - Actions
        right_frame = ttk.LabelFrame(paned_window, text="Actions", padding="5")
        paned_window.add(right_frame, weight=1)
        
        ttk.Button(right_frame, text="Keep This, Delete Others", command=self.keep_selected_delete_others).pack(fill=tk.X, pady=2)
        ttk.Button(right_frame, text="Delete Selected", command=self.delete_selected).pack(fill=tk.X, pady=2)
        ttk.Button(right_frame, text="Move Selected...", command=self.move_selected).pack(fill=tk.X, pady=2)
        ttk.Button(right_frame, text="Rename Selected...", command=self.rename_selected).pack(fill=tk.X, pady=2)
        
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Button(right_frame, text="Close", command=self.duplicate_window.destroy).pack(fill=tk.X, pady=2)
        
        # Select first group if available
        if self.duplicate_groups:
            self.groups_listbox.selection_set(0)
            self.on_group_select(None)
            
    def on_group_select(self, event):
        """Handle group selection in duplicate manager"""
        selection = self.groups_listbox.curselection()
        if not selection:
            return
            
        group_index = selection[0]
        group = self.duplicate_groups[group_index]
        
        # Clear and populate files list
        self.files_listbox.delete(0, tk.END)
        for filepath in group:
            filename = os.path.basename(filepath)
            self.files_listbox.insert(tk.END, f"{filename} ({filepath})")
            
        # Select first file
        if group:
            self.files_listbox.selection_set(0)
            self.on_file_select(None)
            
    def on_file_select(self, event):
        """Handle file selection in duplicate manager"""
        group_selection = self.groups_listbox.curselection()
        file_selection = self.files_listbox.curselection()
        
        if not group_selection or not file_selection:
            return
            
        group_index = group_selection[0]
        file_index = file_selection[0]
        
        filepath = self.duplicate_groups[group_index][file_index]
        
        # Load and display preview if PIL is available
        if PIL_AVAILABLE:
            try:
                with Image.open(filepath) as img:
                    # Resize image for preview
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    self.preview_label.configure(image=photo, text="")
                    self.preview_label.image = photo  # Keep a reference
            except Exception as e:
                self.preview_label.configure(image="", text=f"Cannot preview: {str(e)}")
        else:
            # Show file info instead of preview
            try:
                file_size = os.path.getsize(filepath)
                file_size_mb = file_size / (1024 * 1024)
                file_info = f"File: {os.path.basename(filepath)}\nSize: {file_size_mb:.2f} MB\nPath: {filepath}"
                self.preview_label.configure(image="", text=file_info)
            except Exception as e:
                self.preview_label.configure(image="", text=f"File info unavailable: {str(e)}")
            
    def get_selected_file_info(self):
        """Get currently selected group and file indices"""
        group_selection = self.groups_listbox.curselection()
        file_selection = self.files_listbox.curselection()
        
        if not group_selection or not file_selection:
            messagebox.showwarning("Warning", "Please select a file first.")
            return None, None, None
            
        group_index = group_selection[0]
        file_index = file_selection[0]
        filepath = self.duplicate_groups[group_index][file_index]
        
        return group_index, file_index, filepath
        
    def keep_selected_delete_others(self):
        """Keep selected file and delete all others in the group"""
        group_index, file_index, filepath = self.get_selected_file_info()
        if group_index is None:
            return
            
        group = self.duplicate_groups[group_index]
        
        if messagebox.askyesno("Confirm", f"Keep '{os.path.basename(filepath)}' and delete {len(group)-1} other files?"):
            deleted_count = 0
            for i, file_to_delete in enumerate(group):
                if i != file_index:
                    try:
                        os.remove(file_to_delete)
                        deleted_count += 1
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not delete {file_to_delete}: {str(e)}")
                        
            # Remove this group from the list
            del self.duplicate_groups[group_index]
            
            # Update the groups listbox
            self.groups_listbox.delete(group_index)
            for i in range(group_index, len(self.duplicate_groups)):
                self.groups_listbox.delete(i)
                self.groups_listbox.insert(i, f"Group {i+1}: {len(self.duplicate_groups[i])} files")
                
            messagebox.showinfo("Success", f"Deleted {deleted_count} duplicate files.")
            
            # Select next group if available
            if group_index < self.groups_listbox.size():
                self.groups_listbox.selection_set(group_index)
                self.on_group_select(None)
            elif self.groups_listbox.size() > 0:
                self.groups_listbox.selection_set(self.groups_listbox.size() - 1)
                self.on_group_select(None)
                
    def delete_selected(self):
        """Delete only the selected file"""
        group_index, file_index, filepath = self.get_selected_file_info()
        if group_index is None:
            return
            
        if messagebox.askyesno("Confirm", f"Delete '{os.path.basename(filepath)}'?"):
            try:
                os.remove(filepath)
                
                # Remove file from group
                del self.duplicate_groups[group_index][file_index]
                
                # If group now has only one file, remove the group
                if len(self.duplicate_groups[group_index]) <= 1:
                    del self.duplicate_groups[group_index]
                    self.groups_listbox.delete(group_index)
                    # Update group numbers
                    for i in range(group_index, len(self.duplicate_groups)):
                        self.groups_listbox.delete(i)
                        self.groups_listbox.insert(i, f"Group {i+1}: {len(self.duplicate_groups[i])} files")
                else:
                    # Update group display
                    self.groups_listbox.delete(group_index)
                    self.groups_listbox.insert(group_index, f"Group {group_index+1}: {len(self.duplicate_groups[group_index])} files")
                    
                # Refresh the current selection
                if group_index < len(self.duplicate_groups):
                    self.groups_listbox.selection_set(group_index)
                    self.on_group_select(None)
                elif len(self.duplicate_groups) > 0:
                    self.groups_listbox.selection_set(len(self.duplicate_groups) - 1)
                    self.on_group_select(None)
                    
                messagebox.showinfo("Success", "File deleted successfully.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {str(e)}")
                
    def move_selected(self):
        """Move selected file to another location"""
        group_index, file_index, filepath = self.get_selected_file_info()
        if group_index is None:
            return
            
        dest_folder = filedialog.askdirectory(title="Select destination folder")
        if dest_folder:
            try:
                filename = os.path.basename(filepath)
                dest_path = os.path.join(dest_folder, filename)
                
                # Handle filename conflicts
                if os.path.exists(dest_path):
                    dest_path = os.path.join(dest_folder, self.get_unique_filename(dest_folder, filename))
                    
                shutil.move(filepath, dest_path)
                
                # Remove file from group (same logic as delete)
                del self.duplicate_groups[group_index][file_index]
                
                if len(self.duplicate_groups[group_index]) <= 1:
                    del self.duplicate_groups[group_index]
                    self.groups_listbox.delete(group_index)
                    for i in range(group_index, len(self.duplicate_groups)):
                        self.groups_listbox.delete(i)
                        self.groups_listbox.insert(i, f"Group {i+1}: {len(self.duplicate_groups[i])} files")
                else:
                    self.groups_listbox.delete(group_index)
                    self.groups_listbox.insert(group_index, f"Group {group_index+1}: {len(self.duplicate_groups[group_index])} files")
                    
                if group_index < len(self.duplicate_groups):
                    self.groups_listbox.selection_set(group_index)
                    self.on_group_select(None)
                elif len(self.duplicate_groups) > 0:
                    self.groups_listbox.selection_set(len(self.duplicate_groups) - 1)
                    self.on_group_select(None)
                    
                messagebox.showinfo("Success", f"File moved to {dest_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not move file: {str(e)}")
                
    def rename_selected(self):
        """Rename the selected file"""
        group_index, file_index, filepath = self.get_selected_file_info()
        if group_index is None:
            return
            
        current_name = os.path.basename(filepath)
        new_name = simpledialog.askstring("Rename File", "Enter new filename:", initialvalue=current_name)
        
        if new_name and new_name != current_name:
            try:
                new_path = os.path.join(os.path.dirname(filepath), new_name)
                
                if os.path.exists(new_path):
                    messagebox.showerror("Error", "A file with that name already exists.")
                    return
                    
                os.rename(filepath, new_path)
                
                # Update the file path in the group
                self.duplicate_groups[group_index][file_index] = new_path
                
                # Refresh the display
                self.on_group_select(None)
                
                messagebox.showinfo("Success", "File renamed successfully.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename file: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set up modern styling
    style = ttk.Style()
    
    # Try to use a modern theme if available
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    elif 'alt' in available_themes:
        style.theme_use('alt')
        
    app = PhotoManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()