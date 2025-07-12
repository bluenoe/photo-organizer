#!/usr/bin/env python3
"""
Photo Organizer Script

A robust Python script that automatically organizes photos into a structured
directory based on the date the photos were taken (from EXIF metadata).

Author: Assistant
Version: 1.0
Python: 3.9+
"""

import os
import shutil
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Try to import PIL, but handle gracefully if not available
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL (Pillow) not available. EXIF metadata reading will be disabled.")
    print("Install Pillow with: pip install Pillow")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Supported image file extensions
SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.raw', '.tiff', '.tif', '.bmp', '.gif'
}

# Month names for folder structure
MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def parse_arguments():
    """
    Parse command-line arguments for source and destination directories.
    
    Returns:
        argparse.Namespace: Parsed arguments containing source and destination paths
    """
    parser = argparse.ArgumentParser(
        description='Organize photos by date taken from EXIF metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example usage:
  python photo_organizer.py --source "/path/to/photos" --destination "/path/to/organized"
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Path to the source directory containing unorganized photos'
    )
    
    parser.add_argument(
        '--destination', '-d',
        required=True,
        help='Path to the destination directory for organized photos'
    )
    
    return parser.parse_args()


def extract_date_taken(image_path):
    """
    Extract the 'Date Taken' from image EXIF metadata.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        datetime or None: Date taken if found in EXIF, None otherwise
    """
    if not PIL_AVAILABLE:
        logger.debug(f"PIL not available, skipping EXIF extraction for {image_path}")
        return None
        
    try:
        with Image.open(image_path) as image:
            # Get EXIF data
            exif_data = image._getexif()
            
            if exif_data is not None:
                # Look for DateTime tags in EXIF
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Check for various date/time tags
                    if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        try:
                            # Parse the datetime string (format: 'YYYY:MM:DD HH:MM:SS')
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            continue
                            
    except Exception as e:
        logger.debug(f"Could not extract EXIF data from {image_path}: {e}")
    
    return None


def get_fallback_date(file_path):
    """
    Get the file's last modification date as a fallback.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        datetime: File modification date
    """
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        logger.error(f"Could not get modification date for {file_path}: {e}")
        return datetime.now()  # Ultimate fallback


def create_destination_path(date_obj, destination_root):
    """
    Create the destination path based on date (YYYY/MM-MonthName format).
    
    Args:
        date_obj (datetime): Date object to create path from
        destination_root (str): Root destination directory
        
    Returns:
        str: Full destination directory path
    """
    year = date_obj.strftime('%Y')
    month_num = date_obj.month
    month_name = MONTH_NAMES[month_num]
    month_folder = f"{month_num:02d}-{month_name}"
    
    return os.path.join(destination_root, year, month_folder)


def get_unique_filename(destination_dir, filename):
    """
    Generate a unique filename if a file with the same name already exists.
    
    Args:
        destination_dir (str): Destination directory
        filename (str): Original filename
        
    Returns:
        str: Unique filename
    """
    base_path = os.path.join(destination_dir, filename)
    
    if not os.path.exists(base_path):
        return filename
    
    # Split filename and extension
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(destination_dir, new_filename)
        
        if not os.path.exists(new_path):
            return new_filename
        
        counter += 1


def is_image_file(file_path):
    """
    Check if a file is a supported image type.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is a supported image type
    """
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS


def organize_photos(source_dir, destination_dir):
    """
    Main function to organize photos from source to destination directory.
    
    Args:
        source_dir (str): Source directory containing photos
        destination_dir (str): Destination directory for organized photos
        
    Returns:
        dict: Statistics about the organization process
    """
    stats = {
        'total_scanned': 0,
        'total_moved': 0,
        'total_skipped': 0,
        'exif_used': 0,
        'fallback_used': 0
    }
    
    logger.info(f"Starting photo organization from '{source_dir}' to '{destination_dir}'")
    
    # Walk through all files in source directory recursively
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            stats['total_scanned'] += 1
            
            # Check if it's an image file
            if not is_image_file(file_path):
                logger.debug(f"Skipping non-image file: {file}")
                stats['total_skipped'] += 1
                continue
            
            try:
                # Try to extract date from EXIF
                date_taken = extract_date_taken(file_path)
                
                if date_taken:
                    logger.debug(f"Using EXIF date for {file}: {date_taken}")
                    stats['exif_used'] += 1
                else:
                    # Fallback to file modification date
                    date_taken = get_fallback_date(file_path)
                    logger.debug(f"Using fallback date for {file}: {date_taken}")
                    stats['fallback_used'] += 1
                
                # Create destination directory structure
                dest_dir = create_destination_path(date_taken, destination_dir)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Get unique filename to avoid overwrites
                unique_filename = get_unique_filename(dest_dir, file)
                dest_path = os.path.join(dest_dir, unique_filename)
                
                # Move the file
                shutil.move(file_path, dest_path)
                logger.info(f"Moved: {file} -> {os.path.relpath(dest_path, destination_dir)}")
                stats['total_moved'] += 1
                
            except Exception as e:
                logger.error(f"Error processing {file}: {e}")
                stats['total_skipped'] += 1
    
    return stats


def validate_directories(source_dir, destination_dir):
    """
    Validate that source and destination directories are valid.
    
    Args:
        source_dir (str): Source directory path
        destination_dir (str): Destination directory path
        
    Raises:
        SystemExit: If validation fails
    """
    # Check source directory
    if not os.path.exists(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        raise SystemExit(1)
    
    if not os.path.isdir(source_dir):
        logger.error(f"Source path is not a directory: {source_dir}")
        raise SystemExit(1)
    
    # Create destination directory if it doesn't exist
    try:
        os.makedirs(destination_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Cannot create destination directory {destination_dir}: {e}")
        raise SystemExit(1)


def print_summary(stats):
    """
    Print a summary report of the organization process.
    
    Args:
        stats (dict): Statistics dictionary
    """
    logger.info("\n" + "="*50)
    logger.info("PHOTO ORGANIZATION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total files scanned: {stats['total_scanned']}")
    logger.info(f"Total files moved: {stats['total_moved']}")
    logger.info(f"Total files skipped: {stats['total_skipped']}")
    logger.info(f"Files organized using EXIF data: {stats['exif_used']}")
    logger.info(f"Files organized using fallback date: {stats['fallback_used']}")
    logger.info("="*50)


def main():
    """
    Main function that orchestrates the entire photo organization process.
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Validate directories
        validate_directories(args.source, args.destination)
        
        # Organize photos
        stats = organize_photos(args.source, args.destination)
        
        # Print summary
        print_summary(stats)
        
        logger.info("Photo organization completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
        raise SystemExit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()