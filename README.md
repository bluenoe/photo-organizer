# Face Recognition Photo Organizer (GPU Accelerated & Optimized)

An advanced Python application that automatically organizes your photo collection using state-of-the-art face recognition technology. This tool intelligently detects faces in your images, groups them by unique individuals, and organizes your photos into person-specific folders, with GPU acceleration support and performance optimizations.

## ✨ Key Features

-   **Automatic Face Detection**: Utilizes the powerful `face_recognition` library, supporting both CPU (HOG) and GPU (CNN).
-   **Intelligent Face Grouping**: Advanced face encoding algorithms create unique "fingerprints" for each face and group similar faces.
-   **Interactive Face Naming**: User-friendly graphical user interface (GUI) for naming detected faces.
-   **Multi-Person Support**: Intelligently handles images with multiple people, copying photos to all relevant person folders.
-   **Smart Photo Organization**: Creates an organized folder structure: `Destination/PersonName/photos`.
-   **Performance & Caching**: Parallel processing, enhanced caching system, and GPU acceleration with NVIDIA CUDA.

## 🚀 Installation

### Prerequisites
-   Python 3.7 or higher
-   For GPU acceleration: NVIDIA GPU with CUDA support

### Step 1: Install Python Dependencies
```bash
pip install face_recognition numpy Pillow
```

### Step 2: GPU Setup (Optional)
For significantly faster processing with GPU acceleration, install [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) and [cuDNN](https://developer.nvidia.com/cudnn).

## 📖 Usage Instructions

1.  **Launch the Application**:
    ```bash
    python photo_manager_gui_gpu.py
    ```
2.  **Select Folders**: Choose the source folder and destination folder.
3.  **Configure Settings**: Adjust face recognition tolerance, enable GPU acceleration, set max threads, and resize factor.
4.  **Start Organization**: Click "Start Organization" to begin the process. You will be prompted to name each unique face detected.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for organizing your precious memories - Now with blazing fast performance!**