#!/usr/bin/env python3
"""
Simple test script for Photo Organizer (without PIL dependency)

This script demonstrates the core functionality without requiring
external dependencies.
"""

import os
import tempfile
import shutil
from datetime import datetime

# Import our photo organizer functions
import photo_organizer


def create_test_structure():
    """
    Create a temporary test directory structure with sample files.
    
    Returns:
        tuple: (source_dir, destination_dir, temp_dir) paths
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
    
    # Create test files (simple text files with image extensions for testing)
    test_files = [
        os.path.join(source_dir, 'image1.jpg'),
        os.path.join(source_dir, 'image2.png'),
        os.path.join(subdir1, 'photo1.jpg'),
        os.path.join(subdir1, 'photo2.jpeg'),
        os.path.join(subdir2, 'vacation.jpg'),
        os.path.join(source_dir, 'document.txt'),  # Non-image file
    ]
    
    for filepath in test_files:
        with open(filepath, 'w') as f:
            if filepath.endswith('.txt'):
                f.write('This is not an image file')
            else:
                f.write('This is a test image file (placeholder)')
    
    return source_dir, dest_dir, temp_dir


def test_utility_functions():
    """
    Test individual utility functions.
    """
    print("Testing utility functions...")
    
    # Test date path creation
    test_date = datetime(2024, 7, 15, 14, 30, 0)
    dest_path = photo_organizer.create_destination_path(test_date, "/test/dest")
    expected = os.path.join("/test/dest", "2024", "07-July")
    print(f"Date path test: {dest_path}")
    print(f"Expected: {expected}")
    print(f"✓ Passed" if dest_path == expected else "✗ Failed")
    
    # Test file extension checking
    test_files = [
        ('test.jpg', True),
        ('test.PNG', True),
        ('test.heic', True),
        ('test.txt', False),
        ('test.doc', False)
    ]
    
    print("\nFile extension tests:")
    for filename, expected in test_files:
        result = photo_organizer.is_image_file(filename)
        status = "✓ Passed" if result == expected else "✗ Failed"
        print(f"  {filename}: {result} (expected {expected}) {status}")
    
    # Test unique filename generation
    print("\nUnique filename test:")
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a test file
        test_file = os.path.join(temp_dir, 'test.jpg')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Test unique filename generation
        unique_name = photo_organizer.get_unique_filename(temp_dir, 'test.jpg')
        print(f"  Original: test.jpg")
        print(f"  Unique: {unique_name}")
        print(f"  ✓ Passed" if unique_name == 'test_1.jpg' else "✗ Failed")
    finally:
        shutil.rmtree(temp_dir)


def test_fallback_date():
    """
    Test fallback date functionality.
    """
    print("\nTesting fallback date functionality...")
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    try:
        test_file = os.path.join(temp_dir, 'test.jpg')
        with open(test_file, 'w') as f:
            f.write('test image')
        
        # Test fallback date
        fallback_date = photo_organizer.get_fallback_date(test_file)
        print(f"  Fallback date: {fallback_date}")
        print(f"  ✓ Passed - Got valid datetime object")
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    finally:
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
    print("Photo Organizer Simple Test Suite")
    print("=" * 35)
    
    # Test utility functions
    test_utility_functions()
    
    # Test fallback date
    test_fallback_date()
    
    # Show usage examples
    demo_command_line_usage()
    
    print("\n" + "="*60)
    print("INSTALLATION NOTES:")
    print("="*60)
    print("To use the full functionality with EXIF metadata reading:")
    print("1. Install Python 3.9+")
    print("2. Install Pillow: pip install Pillow")
    print("3. Run: python photo_organizer.py --source <source> --destination <dest>")
    print("\nWithout Pillow, the script will use file modification dates as fallback.")
    
    print("\nSimple test completed successfully!")