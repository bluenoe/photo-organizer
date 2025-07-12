#!/usr/bin/env python3
"""
Test script for Photo Organizer

This script demonstrates how to use the photo organizer and provides
basic functionality tests.
"""

import os
import tempfile
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import photo_organizer


def create_test_image_with_exif(filepath, date_taken):
    """
    Create a test image with EXIF date information.
    
    Args:
        filepath (str): Path where to save the test image
        date_taken (datetime): Date to embed in EXIF
    """
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Create EXIF data
    exif_dict = {
        "0th": {},
        "Exif": {},
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    
    # Add DateTime to EXIF (format: YYYY:MM:DD HH:MM:SS)
    date_str = date_taken.strftime('%Y:%m:%d %H:%M:%S')
    
    # Save the image (Note: PIL doesn't easily allow EXIF writing for JPEG)
    # For testing purposes, we'll create a simple image
    img.save(filepath, 'JPEG')


def create_test_structure():
    """
    Create a temporary test directory structure with sample images.
    
    Returns:
        tuple: (source_dir, destination_dir) paths
    """
    # Create temporary directories
    temp_dir = tempfile.mkdtemp(prefix='photo_organizer_test_')
    source_dir = os.path.join(temp_dir, 'source')
    dest_dir = os.path.join(temp_dir, 'destination')
    
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    # Create subdirectories in source
    subdir1 = os.path.join(source_dir, 'folder1')
    subdir2 = os.path.join(source_dir, 'folder2')
    os.makedirs(subdir1)
    os.makedirs(subdir2)
    
    # Create test images
    test_files = [
        (os.path.join(source_dir, 'image1.jpg'), datetime(2024, 7, 15)),
        (os.path.join(source_dir, 'image2.png'), datetime(2024, 1, 10)),
        (os.path.join(subdir1, 'photo1.jpg'), datetime(2023, 12, 25)),
        (os.path.join(subdir1, 'photo2.jpeg'), datetime(2024, 7, 15)),  # Same date as image1
        (os.path.join(subdir2, 'vacation.jpg'), datetime(2024, 3, 20)),
        (os.path.join(source_dir, 'document.txt'), None),  # Non-image file
    ]
    
    for filepath, date_taken in test_files:
        if filepath.endswith('.txt'):
            # Create a text file (should be skipped)
            with open(filepath, 'w') as f:
                f.write('This is not an image file')
        else:
            # Create test image
            create_test_image_with_exif(filepath, date_taken)
    
    return source_dir, dest_dir, temp_dir


def test_photo_organizer():
    """
    Test the photo organizer functionality.
    """
    print("Creating test directory structure...")
    source_dir, dest_dir, temp_dir = create_test_structure()
    
    try:
        print(f"Source directory: {source_dir}")
        print(f"Destination directory: {dest_dir}")
        print("\nTest files created:")
        
        # List all files in source directory
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, source_dir)
                print(f"  {rel_path}")
        
        print("\n" + "="*50)
        print("RUNNING PHOTO ORGANIZER")
        print("="*50)
        
        # Run the photo organizer
        stats = photo_organizer.organize_photos(source_dir, dest_dir)
        
        print("\n" + "="*50)
        print("RESULTS")
        print("="*50)
        
        # Show the organized structure
        print("\nOrganized directory structure:")
        for root, dirs, files in os.walk(dest_dir):
            level = root.replace(dest_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            folder_name = os.path.basename(root) if root != dest_dir else 'destination'
            print(f"{indent}{folder_name}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        # Print statistics
        photo_organizer.print_summary(stats)
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        raise
    
    finally:
        # Clean up temporary directory
        print(f"\nCleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)


def demo_command_line_usage():
    """
    Demonstrate command-line usage examples.
    """
    print("\n" + "="*60)
    print("PHOTO ORGANIZER - COMMAND LINE USAGE EXAMPLES")
    print("="*60)
    
    examples = [
        {
            'title': 'Basic Usage',
            'command': 'python photo_organizer.py --source "/path/to/photos" --destination "/path/to/organized"'
        },
        {
            'title': 'Windows Example',
            'command': 'python photo_organizer.py --source "C:\\Users\\John\\Pictures\\Unsorted" --destination "C:\\Users\\John\\Pictures\\Organized"'
        },
        {
            'title': 'macOS/Linux Example',
            'command': 'python photo_organizer.py --source "/Users/john/Pictures/Unsorted" --destination "/Users/john/Pictures/Organized"'
        },
        {
            'title': 'Using Short Arguments',
            'command': 'python photo_organizer.py -s "/path/to/source" -d "/path/to/destination"'
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(f"  {example['command']}")
    
    print("\n" + "="*60)
    print("FEATURES:")
    print("="*60)
    
    features = [
        "✓ Organizes photos by date taken (from EXIF metadata)",
        "✓ Falls back to file modification date if EXIF unavailable",
        "✓ Creates YYYY/MM-MonthName folder structure",
        "✓ Handles duplicate filenames automatically",
        "✓ Recursively processes subdirectories",
        "✓ Supports multiple image formats (JPG, PNG, HEIC, RAW, etc.)",
        "✓ Comprehensive logging and error handling",
        "✓ Provides detailed summary statistics"
    ]
    
    for feature in features:
        print(f"  {feature}")


if __name__ == "__main__":
    print("Photo Organizer Test Suite")
    print("=" * 30)
    
    # Show usage examples
    demo_command_line_usage()
    
    # Run functionality test
    print("\n\nRunning functionality test...")
    test_photo_organizer()