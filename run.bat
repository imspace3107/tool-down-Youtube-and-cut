@echo off
echo ========================================
echo    YouTube Video Downloader & Editor
echo ========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy!
    echo Vui lòng cài đặt Python từ https://python.org
    pause
    exit /b 1
)

echo [INFO] Đã tìm thấy Python

REM Kiểm tra FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg không được tìm thấy!
    echo Chức năng cắt video sẽ không hoạt động.
    echo Vui lòng cài đặt FFmpeg và thêm vào PATH.
    echo.
)

REM Kiểm tra requirements
if not exist "requirements.txt" (
    echo [ERROR] Không tìm thấy file requirements.txt
    pause
    exit /b 1
)

echo [INFO] Đang kiểm tra dependencies...
pip show yt-dlp >nul 2>&1
if errorlevel 1 (
    echo [INFO] Đang cài đặt dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Không thể cài đặt dependencies!
        pause
        exit /b 1
    )
)

echo [INFO] Đang khởi động ứng dụng...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ứng dụng gặp lỗi!
    pause
)

echo.
echo Cảm ơn bạn đã sử dụng YouTube Video Downloader!
pause