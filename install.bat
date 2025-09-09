@echo off
echo ========================================
echo    YouTube Video Downloader & Editor
echo           INSTALLATION SCRIPT
echo ========================================
echo.

REM Kiểm tra quyền admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Đang chạy với quyền Administrator
) else (
    echo [INFO] Đang chạy với quyền User
)

echo.
echo [STEP 1] Kiểm tra Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy!
    echo.
    echo Vui lòng:
    echo 1. Tải Python từ https://python.org
    echo 2. Cài đặt Python với tùy chọn "Add to PATH"
    echo 3. Khởi động lại Command Prompt
    echo 4. Chạy lại script này
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Python đã được cài đặt
echo.

echo [STEP 2] Kiểm tra pip...
pip --version
if errorlevel 1 (
    echo [ERROR] pip không được tìm thấy!
    echo Vui lòng cài đặt lại Python với pip
    pause
    exit /b 1
)

echo [SUCCESS] pip đã sẵn sàng
echo.

echo [STEP 3] Cập nhật pip...
python -m pip install --upgrade pip
echo.

echo [STEP 4] Cài đặt dependencies...
if not exist "requirements.txt" (
    echo [ERROR] Không tìm thấy file requirements.txt
    echo Vui lòng đảm bảo bạn đang ở thư mục đúng
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Không thể cài đặt dependencies!
    echo Vui lòng kiểm tra kết nối internet và thử lại
    pause
    exit /b 1
)

echo [SUCCESS] Đã cài đặt tất cả dependencies
echo.

echo [STEP 5] Kiểm tra FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg không được tìm thấy!
    echo.
    echo FFmpeg cần thiết cho chức năng cắt video.
    echo Để cài đặt FFmpeg:
    echo.
    echo CÁCH 1 - Sử dụng Chocolatey (Khuyến nghị):
    echo   1. Cài đặt Chocolatey từ https://chocolatey.org
    echo   2. Chạy: choco install ffmpeg
    echo.
    echo CÁCH 2 - Cài đặt thủ công:
    echo   1. Tải FFmpeg từ https://ffmpeg.org/download.html
    echo   2. Giải nén và thêm thư mục bin vào PATH
    echo.
    echo Bạn có thể bỏ qua bước này nếu chỉ muốn tải video không cắt.
    echo.
) else (
    echo [SUCCESS] FFmpeg đã được cài đặt
    ffmpeg -version | findstr "ffmpeg version"
)

echo.
echo ========================================
echo           CÀI ĐẶT HOÀN TẤT!
echo ========================================
echo.
echo Để chạy ứng dụng:
echo   - Nhấp đúp vào run.bat
echo   - Hoặc chạy: python main.py
echo.
echo Để xem hướng dẫn chi tiết:
echo   - Mở file README.md
echo.
echo Chúc bạn sử dụng vui vẻ!
echo.
pause