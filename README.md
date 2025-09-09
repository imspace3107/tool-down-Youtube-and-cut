# YouTube Video Downloader & Editor

Ứng dụng desktop để tải và chỉnh sửa video YouTube với giao diện thân thiện.

## Tính năng chính

### Tab 1: YouTube Downloader
- ✅ Nhập nhiều đường link YouTube cùng lúc
- ✅ Tải video ở độ phân giải từ 720p đến 1440p
- ✅ Giữ nguyên FPS theo độ phân giải gốc của video
- ✅ Cắt video ngẫu nhiên theo thời gian tùy chỉnh
- ✅ Xử lý đặc biệt cho video ngắn
- ✅ Thanh tiến trình chi tiết cho từng quá trình
- ✅ Log chi tiết và hiển thị kết quả

### Tab 2: Future Features
- 🚧 Tải video từ Xiaohongsu (đang phát triển)
- 🚧 Tải video từ Vbeef ở độ phân giải cao nhất (đang phát triển)

## Yêu cầu hệ thống

- **Python**: 3.8 trở lên
- **FFmpeg**: Cần cài đặt FFmpeg và thêm vào PATH
- **Hệ điều hành**: Windows, macOS, Linux

## Cài đặt

### 1. Cài đặt Python
Tải và cài đặt Python từ [python.org](https://python.org)

### 2. Cài đặt FFmpeg

#### Windows:
1. Tải FFmpeg từ [ffmpeg.org](https://ffmpeg.org/download.html)
2. Giải nén và thêm thư mục `bin` vào PATH
3. Hoặc sử dụng chocolatey: `choco install ffmpeg`

#### macOS:
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Cài đặt dependencies

```bash
# Clone hoặc tải project
cd new_tool

# Cài đặt các thư viện Python
pip install -r requirements.txt
```

## Sử dụng

### Chạy ứng dụng
```bash
python main.py
```

### Hướng dẫn sử dụng

#### 1. Tải video YouTube

1. **Nhập link video:**
   - Mở tab "YouTube Downloader"
   - Nhập các đường link YouTube vào ô text (mỗi link một dòng)
   - Nhấn "Thêm Link" để xác nhận

2. **Cài đặt tải video:**
   - Chọn thư mục lưu file
   - Chọn độ phân giải: 720p, 1080p, hoặc 1440p

3. **Cài đặt cắt video (tùy chọn):**
   - Tích "Bật cắt video ngẫu nhiên"
   - Đặt thời gian tối thiểu và tối đa (giây)
   - Đặt thời gian cho video ngắn

4. **Bắt đầu tải:**
   - Nhấn "Bắt Đầu Tải"
   - Theo dõi tiến trình qua thanh progress và log
   - Có thể nhấn "Dừng" để hủy bỏ

#### 2. Logic cắt video

- **Video dài** (> thời gian ngưỡng): Cắt ngẫu nhiên từ min đến max giây
- **Video ngắn** (≤ thời gian ngưỡng): Lấy từ đầu video với độ dài = thời gian ngưỡng

#### 3. Kết quả

- Video được lưu trong thư mục đã chọn
- Tên file bao gồm tiêu đề và ID video
- Video cắt có thêm hậu tố "_cut"
- Log hiển thị chi tiết kích thước và đường dẫn file

## Cấu trúc project

```
new_tool/
├── main.py              # File chính chứa GUI
├── video_downloader.py  # Module xử lý tải và cắt video
├── requirements.txt     # Danh sách dependencies
└── README.md           # Hướng dẫn này
```

## Dependencies

- **yt-dlp**: Tải video từ YouTube và các platform khác
- **ffmpeg-python**: Wrapper Python cho FFmpeg
- **tkinter**: GUI framework (built-in với Python)
- **tqdm**: Thanh tiến trình
- **requests**: HTTP requests
- **Pillow**: Xử lý hình ảnh
- **opencv-python**: Xử lý video

## Xử lý lỗi thường gặp

### 1. Lỗi "FFmpeg not found"
**Giải pháp:** Cài đặt FFmpeg và thêm vào PATH

### 2. Lỗi "No module named 'yt_dlp'"
**Giải pháp:** 
```bash
pip install -r requirements.txt
```

### 3. Video không tải được
**Nguyên nhân có thể:**
- Link không hợp lệ
- Video bị hạn chế địa lý
- Video riêng tư
- Kết nối internet không ổn định

### 4. Lỗi cắt video
**Nguyên nhân có thể:**
- File video bị lỗi
- Không đủ dung lượng ổ cứng
- FFmpeg không hoạt động đúng

## Tính năng nâng cao

### Tùy chỉnh format video
Có thể chỉnh sửa `video_downloader.py` để:
- Thay đổi codec video
- Tùy chỉnh bitrate
- Thêm subtitle
- Chọn format audio

### Batch processing
Ứng dụng hỗ trợ xử lý nhiều video cùng lúc với:
- Thanh tiến trình tổng thể
- Log chi tiết cho từng video
- Xử lý lỗi riêng biệt

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

Project này được phát hành dưới MIT License.

## Liên hệ

Nếu có vấn đề hoặc đề xuất, vui lòng tạo issue trên GitHub.

---

**Lưu ý:** Vui lòng tuân thủ các điều khoản sử dụng của YouTube và các platform khác khi sử dụng ứng dụng này.