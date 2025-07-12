# Photo Organizer

A robust Python script that automatically organizes photos into a structured directory based on the date the photos were taken (extracted from EXIF metadata).

## Features

- **EXIF-based Organization**: Uses photo metadata to determine when photos were taken
- **Fallback Date Handling**: Uses file modification date when EXIF data is unavailable
- **Structured Output**: Organizes photos into `YYYY/MM-MonthName/` folder structure
- **Duplicate Handling**: Automatically renames files to prevent overwrites
- **Recursive Scanning**: Processes all subdirectories in the source folder
- **Comprehensive Logging**: Detailed progress reporting and error handling
- **Multiple Format Support**: Supports JPG, PNG, HEIC, RAW, TIFF, BMP, and GIF files

## Requirements

- Python 3.9 or higher
- Pillow (PIL Fork) for image processing

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python photo_organizer.py --source "/path/to/source/photos" --destination "/path/to/organized/photos"
```

### Command Line Arguments

- `--source` or `-s`: Path to the source directory containing unorganized photos (required)
- `--destination` or `-d`: Path to the destination directory for organized photos (required)

### Example

```bash
# Windows
python photo_organizer.py --source "C:\Users\John\Pictures\Unsorted" --destination "C:\Users\John\Pictures\Organized"

# macOS/Linux
python photo_organizer.py --source "/Users/john/Pictures/Unsorted" --destination "/Users/john/Pictures/Organized"
```

## Output Structure

The script organizes photos into the following structure:

```
Destination/
├── 2024/
│   ├── 01-January/
│   │   ├── IMG_001.jpg
│   │   └── IMG_002.jpg
│   ├── 02-February/
│   │   └── IMG_003.jpg
│   └── 07-July/
│       ├── IMG_004.jpg
│       └── IMG_005.jpg
└── 2023/
    └── 12-December/
        └── IMG_006.jpg
```

## How It Works

1. **Scanning**: Recursively scans the source directory for image files
2. **Date Extraction**: Attempts to extract the "Date Taken" from EXIF metadata
3. **Fallback**: If EXIF data is unavailable, uses the file's last modification date
4. **Organization**: Creates year/month folder structure and moves files
5. **Duplicate Handling**: Appends numeric suffixes to prevent file overwrites
6. **Reporting**: Provides detailed logging and summary statistics

## Supported File Types

- JPEG (.jpg, .jpeg)
- PNG (.png)
- HEIC (.heic)
- RAW (.raw)
- TIFF (.tiff, .tif)
- BMP (.bmp)
- GIF (.gif)

## Logging

The script provides comprehensive logging including:

- Files being processed and their destinations
- Files skipped (non-image files)
- Errors encountered during processing
- Summary statistics at completion

## Error Handling

- Validates source and destination directories
- Handles missing EXIF data gracefully
- Prevents file overwrites with automatic renaming
- Provides clear error messages for troubleshooting

## Safety Features

- **No Overwrites**: Files with duplicate names are automatically renamed
- **Validation**: Checks directory paths before processing
- **Graceful Errors**: Continues processing even if individual files fail
- **Detailed Logging**: Tracks all operations for transparency

## Example Output

```
2024-01-15 10:30:15 - INFO - Starting photo organization from 'C:\Photos\Unsorted' to 'C:\Photos\Organized'
2024-01-15 10:30:16 - INFO - Moved: IMG_1234.jpg -> 2024/07-July/IMG_1234.jpg
2024-01-15 10:30:16 - INFO - Moved: DSC_5678.jpg -> 2024/07-July/DSC_5678.jpg
2024-01-15 10:30:17 - INFO - Moved: photo.png -> 2023/12-December/photo.png

==================================================
PHOTO ORGANIZATION SUMMARY
==================================================
Total files scanned: 150
Total files moved: 142
Total files skipped: 8
Files organized using EXIF data: 135
Files organized using fallback date: 7
==================================================
```

## License

This project is open source and available under the MIT License.