# Face Recognition Photo Organizer (GPU Accelerated & Optimized)

An advanced Python application that automatically organizes your photo collection using state-of-the-art face recognition technology. This tool intelligently detects faces in your images, groups them by unique individuals, and organizes your photos into person-specific folders with GPU acceleration support and performance optimizations for handling large datasets.

## ✨ Key Features

### 🎯 **Automatic Face Detection**
- Utilizes the powerful `face_recognition` library built on dlib's deep learning models
- Supports both CPU (HOG) and GPU (CNN) face detection models
- Automatically detects and extracts faces from images with high accuracy
- Handles multiple faces per image seamlessly
- **NEW**: Image resizing for faster processing without quality loss

### 🧠 **Intelligent Face Grouping**
- Advanced face encoding algorithms create unique "fingerprints" for each face
- **NEW**: Vectorized face comparison for 3-5x faster grouping
- Automatically groups similar faces using configurable tolerance levels
- Eliminates duplicate face processing across your entire photo collection
- Smart similarity detection prevents over-grouping or under-grouping

### 👤 **Interactive Face Naming**
- User-friendly GUI for naming detected faces
- **NEW**: Enhanced face preview with better image handling and centering
- Visual face preview windows for easy identification
- Clean, intuitive interface for managing large numbers of unique faces
- Skip option for faces you don't want to organize

### 👥 **Multi-Person Support**
- Single images containing multiple people are copied to all relevant person folders
- Comprehensive organization ensures no photos are missed
- Handles complex family photos and group pictures intelligently

### 📁 **Smart Photo Organization**
- Creates organized folder structure: `Destination/PersonName/photos`
- Automatic duplicate filename handling with intelligent numbering
- Preserves original image metadata and quality
- Non-destructive copying (originals remain untouched)
- **NEW**: Batch processing for better memory management

### ⚡ **Performance & Caching**
- **NEW**: Parallel processing with ThreadPoolExecutor for multi-core utilization
- **NEW**: Enhanced caching system with memory and disk cache layers
- **NEW**: Automatic cache cleanup to prevent unlimited growth
- GPU acceleration support with NVIDIA CUDA
- **NEW**: Non-blocking UI with real-time progress updates
- **NEW**: Stop/resume functionality for long-running operations
- Optimized for large photo collections (500-1000+ images)

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- For GPU acceleration: NVIDIA GPU with CUDA support
- Recommended: 8GB+ RAM for large image collections

### Step 1: Install Python Dependencies
```bash
pip install face_recognition numpy Pillow
```

### Step 2: GPU Setup (Optional but Recommended)
For significantly faster processing with GPU acceleration:

#### Install CUDA Toolkit
1. Download and install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
2. Ensure your NVIDIA drivers are up to date

#### Install cuDNN
1. Download [cuDNN](https://developer.nvidia.com/cudnn) (requires NVIDIA account)
2. Extract and copy files to your CUDA installation directory

#### Verify GPU Setup
```python
import dlib
print(f"CUDA available: {dlib.DLIB_USE_CUDA}")
print(f"GPU devices: {dlib.cuda.get_num_devices()}")
```

### Platform-Specific Installation

#### Windows
```bash
# Install Visual Studio Build Tools if needed
pip install cmake
pip install face_recognition
```

#### macOS
```bash
brew install cmake boost-python3
pip install face_recognition
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install face_recognition
```

## 📖 Usage Instructions

### Basic Usage
1. **Launch the Application**
   ```bash
   python photo_manager_gui_gpu.py
   ```

2. **Select Folders**
   - **Source Folder**: Choose the folder containing your photos to organize
   - **Destination Folder**: Choose where you want the organized folders to be created

3. **Configure Settings**
   - **Face Recognition Tolerance**: Adjust similarity threshold (lower = more strict matching)
   - **GPU Acceleration**: Enable if you have a compatible NVIDIA GPU setup
   - **Max Threads**: Configure parallel processing (default: CPU cores, max: 16)
   - **Resize Factor**: Adjust image resizing for speed vs. accuracy (0.25-1.0)

4. **Start Organization**
   - Click "Start Organization" to begin the process
   - **NEW**: Use "Stop Processing" to halt operation at any time
   - The tool will scan all images and detect faces using parallel processing
   - You'll be prompted to name each unique face detected
   - Photos will be automatically organized into person-specific folders

### Advanced Features
- **Cache Management**: Use "Clear Cache" to reset face encodings if you want to reprocess images
- **Tolerance Tuning**: Lower values (0.3-0.5) for stricter matching, higher values (0.6-0.8) for more lenient matching
- **GPU Acceleration**: Significantly faster processing for large image collections
- **Performance Tuning**: Adjust thread count and resize factor based on your system capabilities

## 📋 Supported File Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **BMP** (.bmp)
- **TIFF** (.tiff)
- **WebP** (.webp)

## 🔧 Technical Features

### Face Recognition Technology
- **Deep Learning Models**: Uses state-of-the-art CNN models for face detection
- **Face Encoding**: 128-dimensional face embeddings for accurate comparison
- **Similarity Matching**: Euclidean distance-based face comparison
- **Multi-scale Detection**: Handles faces of various sizes and orientations
- **Smart Filtering**: Automatically filters out very small faces

### Performance Optimizations
- **Parallel Processing**: Multi-threaded face detection and encoding
- **Intelligent Caching**: Two-tier cache system (memory + disk)
- **Image Resizing**: Automatic resizing for faster processing
- **Batch Processing**: Processes images in configurable batches
- **Vectorized Operations**: NumPy-optimized face comparisons
- **GPU Acceleration**: CUDA-enabled processing for 3-5x speed improvement
- **Memory Management**: Efficient handling of large image collections
- **Progress Tracking**: Real-time updates on processing status

### Security & Privacy
- **Local Processing**: All face recognition happens on your local machine
- **No Cloud Upload**: Your photos never leave your computer
- **Original Preservation**: Source images remain completely untouched
- **Metadata Preservation**: EXIF data and timestamps are maintained

## 🛠️ Troubleshooting

### Common Issues

#### "face_recognition not found"
```bash
pip install --upgrade face_recognition
```

#### GPU not detected
- Verify NVIDIA drivers are installed and up to date
- Ensure CUDA Toolkit is properly installed
- Check that dlib was compiled with CUDA support
- Restart the application after GPU setup

#### Slow processing
- Enable GPU acceleration if available
- Increase thread count (up to CPU cores)
- Reduce resize factor for faster processing
- Close other resource-intensive applications
- Consider processing smaller batches of images

#### Memory errors with large collections
- Reduce batch size in performance settings
- Lower thread count to reduce memory usage
- Clear cache between runs
- Ensure sufficient RAM (8GB+ recommended for large collections)
- Close other applications to free memory

#### UI freezing
- **NEW**: The optimized version uses non-blocking UI
- Use the "Stop Processing" button if needed
- Check system resources and reduce thread count if necessary

### Performance Tips
- **GPU Acceleration**: Can provide 3-5x speed improvement
- **Parallel Processing**: Utilize all CPU cores for maximum speed
- **Image Resizing**: Lower resize factor = faster processing
- **Batch Processing**: Optimal batch size is 50-100 images
- **Cache Utilization**: Subsequent runs on the same images are much faster

## 🏗️ Code Architecture

### Core Components
- **`OptimizedFaceRecognitionOrganizer`**: Main application class with performance optimizations
- **`OptimizedFaceEncodingCache`**: Enhanced two-tier caching system
- **`FaceData`**: Data structure representing detected faces with metadata and caching
- **GUI Components**: Tkinter-based user interface with real-time progress tracking
- **Threading System**: Background processing with queue-based communication

### Key Methods
- `extract_face_encodings_optimized()`: Parallel face detection with caching
- `find_unique_faces_optimized()`: Vectorized face grouping with batch processing
- `organize_photos_optimized()`: Efficient photo organization with progress tracking
- `process_image_batch()`: Parallel processing of image batches
- `group_similar_faces_optimized()`: Vectorized face similarity calculations

### Design Patterns
- **Producer-Consumer**: Queue-based communication between threads
- **Caching Strategy**: Multi-tier caching for optimal performance
- **Observer Pattern**: Progress updates and status notifications
- **Strategy Pattern**: Configurable face detection models and performance settings
- **Factory Pattern**: Dynamic creation of face data objects
- **Thread Pool Pattern**: Managed parallel processing

## 🤝 Contributing

We welcome contributions to improve this tool! Here's how you can help:

### Areas for Contribution
- **Performance Optimizations**: Further speed improvements
- **UI/UX Enhancements**: Better user interface design
- **Additional File Formats**: Support for more image types
- **Advanced Features**: Batch naming, face clustering improvements
- **Documentation**: Improved guides and tutorials
- **Testing**: Performance benchmarks and edge case testing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

### Code Standards
- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings for new functions
- Include error handling for edge cases
- Test with various image types and sizes
- Performance test with large datasets

## 📝 Changelog

### Version 3.0 (Current - Optimized)
- ✅ **NEW**: Parallel processing with ThreadPoolExecutor
- ✅ **NEW**: Image resizing for faster face detection
- ✅ **NEW**: Vectorized face grouping algorithms
- ✅ **NEW**: Non-blocking UI with stop/resume functionality
- ✅ **NEW**: Enhanced two-tier caching system
- ✅ **NEW**: Batch processing for memory optimization
- ✅ **NEW**: Performance settings (threads, resize factor)
- ✅ **NEW**: Automatic cache cleanup
- ✅ **NEW**: Better error handling and timeout management
- ✅ **NEW**: Support for larger image collections (500-1000+)

### Version 2.1
- ✅ Added GPU acceleration support with CNN model
- ✅ Enhanced face detection accuracy
- ✅ Improved error handling and user feedback
- ✅ Better progress tracking and status updates
- ✅ Optimized memory usage for large collections

### Version 2.0
- ✅ Complete GUI redesign with modern interface
- ✅ Advanced caching system for improved performance
- ✅ Multi-person support in single images
- ✅ Configurable face recognition tolerance
- ✅ Enhanced error handling and logging

### Version 1.0
- ✅ Basic face recognition and photo organization
- ✅ Simple command-line interface
- ✅ Core face detection and grouping functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues or have questions:

1. **Check the Troubleshooting section** above for common solutions
2. **Review the logs** in `face_organizer.log` for detailed error information
3. **Create an issue** on GitHub with:
   - Your operating system and Python version
   - Complete error messages
   - Steps to reproduce the problem
   - Sample images (if privacy allows)
   - Performance settings used

---

**Made with ❤️ for organizing your precious memories - Now with blazing fast performance!**