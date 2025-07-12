# Face Recognition Photo Organizer

An advanced photo organization tool that uses face recognition to automatically sort your photo library by detecting and grouping photos of the same people. Built with Python and featuring a modern GUI interface.

## Features

### Core Functionality
- **Automatic Face Detection**: Scans all images for human faces using state-of-the-art face recognition
- **Intelligent Face Grouping**: Groups similar faces together with high accuracy
- **Interactive Face Naming**: Shows cropped face previews for easy identification and naming
- **Multi-Person Support**: Handles multiple faces per image - copies photos to multiple person folders
- **Smart Organization**: Creates person-specific folders with automatic duplicate handling
- **Performance Caching**: Caches face encodings for faster repeated runs
- **Modern GUI**: Clean, user-friendly interface with real-time progress tracking

### Face Recognition Process
1. **Image Scanning**: Recursively finds all JPEG and PNG images in the source folder
2. **Face Detection**: Uses advanced algorithms to detect all faces in each image
3. **Face Grouping**: Groups similar faces together using face distance calculations
4. **Interactive Naming**: Displays face previews and prompts for person names
5. **Smart Organization**: Copies images to person-named folders (supports multiple people per image)

## Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.9 trở lên
- Windows/macOS/Linux

### Cài Đặt Thư Viện

#### Cài đặt cơ bản (không có nhận diện khuôn mặt):
```bash
pip install Pillow
```

#### Cài đặt đầy đủ (có nhận diện khuôn mặt):
```bash
pip install -r requirements.txt
```

#### Lưu ý cho Windows:
Nếu gặp lỗi khi cài `face_recognition`, hãy thử:
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

Hoặc sử dụng pre-compiled wheels:
```bash
pip install --upgrade pip
pip install face_recognition
```

## Sử Dụng

### Khởi Chạy Ứng Dụng
```bash
python photo_manager_gui.py
```

### Hướng Dẫn Sử Dụng

1. **Chọn thư mục nguồn**: Thư mục chứa ảnh cần sắp xếp
2. **Chọn thư mục đích**: Nơi lưu ảnh đã được sắp xếp
3. **Chọn tùy chọn**:
   - ✅ **Find & Manage Duplicates**: Tìm và quản lý file trùng lặp
   - ✅ **Group by Face Recognition**: Nhóm ảnh theo khuôn mặt (MỚI!)
   - ✅ **Group by Similar Name**: Nhóm ảnh theo tên tương tự
4. **Nhấn "Start Organizing"**

### Quy Trình Nhận Diện Khuôn Mặt

1. **Quét ảnh**: Ứng dụng sẽ quét tất cả ảnh để tìm khuôn mặt
2. **Đặt tên**: Cửa sổ popup hiện ra cho phép bạn đặt tên cho từng khuôn mặt
   - Xem preview khuôn mặt đã cắt
   - Nhập tên cho mỗi khuôn mặt
   - Các khuôn mặt giống nhau sẽ được nhóm lại
3. **Sắp xếp**: Ảnh sẽ được sắp xếp vào thư mục theo cấu trúc:
   ```
   YYYY/
   └── MM-TênTháng/
       ├── TênNgười1/
       ├── TênNgười2/
       └── ...
   ```

### Ví Dụ Cấu Trúc Thư Mục Kết Quả

```
Destination/
├── 2024/
│   ├── 01-January/
│   │   ├── Minh/
│   │   │   ├── IMG_001.jpg
│   │   │   └── IMG_005.jpg
│   │   ├── Lan/
│   │   │   ├── IMG_002.jpg
│   │   │   └── IMG_006.jpg
│   │   └── IMG_003.jpg (không có khuôn mặt)
│   └── 02-February/
│       ├── Minh/
│       └── Lan/
└── 2023/
    └── 12-December/
        ├── Minh/
        └── Family_Group/
```

## Định Dạng File Hỗ Trợ

- **Ảnh**: JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP
- **Video**: MP4, AVI, MOV, MKV, WMV, FLV

## Tính Năng Kỹ Thuật

- **Xử lý lỗi mạnh mẽ**: Tiếp tục xử lý khi gặp file lỗi
- **Hiệu suất cao**: Xử lý hàng nghìn file một cách hiệu quả
- **Tương thích đa nền tảng**: Chạy trên Windows, macOS, Linux
- **Giao diện thân thiện**: Thiết kế hiện đại với thanh tiến trình
- **Phát hiện trùng lặp dựa trên nội dung**: Sử dụng MD5 hash
- **Nhận diện khuôn mặt chính xác**: Sử dụng deep learning

## Xử Lý Sự Cố

### Lỗi Cài Đặt face_recognition

**Windows:**
```bash
# Cài đặt Visual Studio Build Tools
# Hoặc sử dụng conda:
conda install -c conda-forge dlib
conda install -c conda-forge face_recognition
```

**macOS:**
```bash
brew install cmake
pip install face_recognition
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install face_recognition
```

### Ứng Dụng Chạy Chậm
- Giảm số lượng ảnh xử lý trong một lần
- Đảm bảo đủ RAM (khuyến nghị 4GB+)
- Sử dụng SSD thay vì HDD

### Nhận Diện Khuôn Mặt Không Chính Xác
- Đảm bảo ảnh có độ phân giải đủ cao
- Khuôn mặt phải rõ ràng và không bị che khuất
- Ánh sáng đủ sáng

## Phát Triển

### Cấu Trúc Code
- `photo_manager_gui.py`: File chính chứa toàn bộ ứng dụng
- `requirements.txt`: Danh sách thư viện cần thiết
- `README.md`: Tài liệu hướng dẫn

### Đóng Góp
Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## Giấy Phép
Mã nguồn mở - sử dụng tự do cho mục đích cá nhân và thương mại.

## Liên Hệ
Nếu có thắc mắc hoặc cần hỗ trợ, vui lòng tạo issue trên GitHub.