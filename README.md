# Face Recognition Photo Organizer (GPU Accelerated & Optimized)

Ứng dụng Python tiên tiến giúp tự động sắp xếp bộ sưu tập ảnh của bạn bằng công nghệ nhận diện khuôn mặt hiện đại. Công cụ này phát hiện khuôn mặt trong ảnh, nhóm chúng theo từng cá nhân và sắp xếp ảnh vào các thư mục riêng cho từng người, với hỗ trợ tăng tốc GPU và tối ưu hóa hiệu suất.

## ✨ Tính năng chính

-   **Phát hiện khuôn mặt tự động**: Sử dụng thư viện `face_recognition` mạnh mẽ, hỗ trợ cả CPU (HOG) và GPU (CNN).
-   **Nhóm khuôn mặt thông minh**: Thuật toán mã hóa khuôn mặt tiên tiến tạo ra "dấu vân tay" độc đáo cho mỗi khuôn mặt và nhóm các khuôn mặt tương tự.
-   **Đặt tên khuôn mặt tương tác**: Giao diện người dùng đồ họa (GUI) thân thiện để đặt tên cho các khuôn mặt được phát hiện.
-   **Hỗ trợ nhiều người**: Xử lý thông minh các ảnh có nhiều người, sao chép ảnh vào tất cả các thư mục người liên quan.
-   **Tổ chức ảnh thông minh**: Tạo cấu trúc thư mục có tổ chức: `Destination/PersonName/photos`.
-   **Hiệu suất & Bộ nhớ đệm**: Xử lý song song, hệ thống bộ nhớ đệm nâng cao và tăng tốc GPU với NVIDIA CUDA.

## 🚀 Cài đặt

### Điều kiện tiên quyết
-   Python 3.7 trở lên
-   Để tăng tốc GPU: GPU NVIDIA có hỗ trợ CUDA

### Bước 1: Cài đặt các phụ thuộc của Python
```bash
pip install face_recognition numpy Pillow
```

### Bước 2: Thiết lập GPU (Tùy chọn)
Để xử lý nhanh hơn đáng kể với tăng tốc GPU, hãy cài đặt [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) và [cuDNN](https://developer.nvidia.com/cudnn).

## 📖 Hướng dẫn sử dụng

1.  **Khởi chạy ứng dụng**:
    ```bash
    python photo_manager_gui_gpu.py
    ```
2.  **Chọn thư mục**: Chọn thư mục nguồn và thư mục đích.
3.  **Cấu hình cài đặt**: Điều chỉnh dung sai nhận diện khuôn mặt, bật tăng tốc GPU, đặt số luồng tối đa và hệ số thay đổi kích thước ảnh.
4.  **Bắt đầu tổ chức**: Nhấp vào "Start Organization" để bắt đầu quá trình. Bạn sẽ được nhắc đặt tên cho từng khuôn mặt duy nhất được phát hiện.

## 📄 Giấy phép

Dự án này được cấp phép theo Giấy phép MIT - xem tệp [LICENSE](LICENSE) để biết chi tiết.

---

**Được tạo ra với ❤️ để sắp xếp những kỷ niệm quý giá của bạn - Giờ đây với hiệu suất cực nhanh!**