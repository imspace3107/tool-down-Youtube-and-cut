#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File cấu hình cho ứng dụng YouTube Video Downloader
Chứa tất cả các thông số setting để dễ quản lý
"""

import os
from pathlib import Path

class Config:
    """Class chứa tất cả cấu hình của ứng dụng"""
    
    # ===== CẤU HÌNH ĐƯỜNG DẪN =====
    # Thư mục mặc định để lưu video
    DEFAULT_DOWNLOAD_DIR = r'E:\tool-down-Youtube-and-cut\downloads'
    
    # Thư mục lưu log
    LOG_DIR = "logs"
    LOG_FILE = "app_debug.log"
    
    # ===== CẤU HÌNH CẮT VIDEO =====
    # Thời gian cắt video (giây)
    MIN_CUT_TIME = 71
    MAX_CUT_TIME = 73
    
    # Ngưỡng video ngắn (giây) - video ngắn hơn sẽ không bị cắt
    SHORT_VIDEO_THRESHOLD = 0
    
    # Ngưỡng nối đoạn cuối (giây) - nếu đoạn cuối < ngưỡng này sẽ nối vào đoạn trước
    MERGE_LAST_SEGMENT_THRESHOLD = 59
    
    # Buffer time để tránh lỗi khi cắt (giây)
    CUT_BUFFER_TIME = 2.0
    
    # ===== CẤU HÌNH VIDEO SPLITTER =====
    # Thời gian mỗi đoạn video (giây) - không sử dụng nữa, dùng MIN_CUT_TIME/MAX_CUT_TIME
    SEGMENT_DURATION = 90  # 1 phút 30 giây (deprecated)
    
    # Thời gian tối thiểu cho đoạn cuối
    MIN_LAST_SEGMENT_DURATION = 30
    
    # Đường dẫn output cho VideoSplitter
    OUTPUT_PATH = "downloads"

    # ===== CẤU HÌNH XIAOHONGSHU =====
    # Thư mục lưu video Xiaohongshu
    XIAOHONGSHU_OUTPUT_DIR = "downloads/xiaohongshu"
    
    # Timeout cho request Xiaohongshu (giây)
    XIAOHONGSHU_TIMEOUT = 30
    
    # Số lần thử lại khi tải thất bại
    XIAOHONGSHU_RETRY_COUNT = 3
    
    # User Agent cho Xiaohongshu
    XIAOHONGSHU_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # ===== CẤU HÌNH CHẤT LƯỢNG VIDEO =====
    # Độ phân giải mặc định
    DEFAULT_RESOLUTION = '1080p'
    
    # Danh sách độ phân giải hỗ trợ
    SUPPORTED_RESOLUTIONS = ["1440p", "1080p", "720p"]
    RESOLUTION_OPTIONS = ["Best", "1440p", "1080p", "720p"]
    
    # Thư mục output mặc định
    DEFAULT_OUTPUT_DIR = str(Path(__file__).parent / "downloads")
    
    # ===== CẤU HÌNH FFMPEG =====
    # Codec video
    VIDEO_CODEC = "libx264"
    
    # Codec audio
    AUDIO_CODEC = "aac"
    
    # Preset encoding (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
    ENCODING_PRESET = "medium"
    
    # CRF (Constant Rate Factor) - chất lượng video (0-51, thấp hơn = chất lượng cao hơn)
    CRF_VALUE = 18
    
    # ===== CẤU HÌNH YT-DLP =====
    # Format selector cho từng độ phân giải
    FORMAT_SELECTORS = {
        "Best": "bestvideo[height<=1440][height>=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1440][height>=720]+bestaudio/best[height<=1440][height>=720]",
        "1440p": "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best[height<=1440]",
        "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]"
    }
    
    # Cấu hình yt-dlp
    YT_DLP_OPTIONS = {
        'format_sort': ['filesize'],
        'format_sort_force': False,
        'merge_output_format': 'mp4',
        'writeinfojson': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
        'no_warnings': False,
        'extractflat': False,
        'writethumbnail': False,
        'outtmpl': '%(title)s_%(id)s.%(ext)s'
    }
    
    # ===== CẤU HÌNH GIAO DIỆN =====
    # Kích thước cửa sổ mặc định
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 800
    
    # Tiêu đề ứng dụng
    APP_TITLE = "YouTube Video Downloader & Editor"
    
    # ===== CẤU HÌNH LOGGING =====
    # Level logging
    LOG_LEVEL = "DEBUG"
    
    # Format log
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Encoding cho file log
    LOG_ENCODING = 'utf-8'
    
    # ===== CẤU HÌNH KHÁC =====
    # Số lượng video tối đa có thể tải cùng lúc
    MAX_CONCURRENT_DOWNLOADS = 3
    
    # Timeout cho mỗi video (giây)
    DOWNLOAD_TIMEOUT = 300
    
    # Có xóa file gốc sau khi cắt không
    DELETE_ORIGINAL_AFTER_CUT = False
    
    # Tên thư mục chứa các đoạn video đã cắt
    SEGMENTS_FOLDER_SUFFIX = "_segments"
    
    # Format tên file đoạn video
    SEGMENT_NAME_FORMAT = "{base_name}_part{index:02d}.mp4"
    
    @classmethod
    def get_log_file_path(cls):
        """Lấy đường dẫn đầy đủ của file log"""
        if cls.LOG_DIR:
            os.makedirs(cls.LOG_DIR, exist_ok=True)
            return os.path.join(cls.LOG_DIR, cls.LOG_FILE)
        return cls.LOG_FILE
    
    @classmethod
    def get_segments_dir_name(cls, base_name):
        """Lấy tên thư mục chứa các đoạn video"""
        return f"{base_name}{cls.SEGMENTS_FOLDER_SUFFIX}"
    
    @classmethod
    def get_segment_filename(cls, base_name, index):
        """Lấy tên file đoạn video"""
        return cls.SEGMENT_NAME_FORMAT.format(base_name=base_name, index=index)
    
    @classmethod
    def validate_resolution(cls, resolution):
        """Kiểm tra độ phân giải có hợp lệ không"""
        return resolution in cls.SUPPORTED_RESOLUTIONS
    
    @classmethod
    def get_format_selector(cls, resolution):
        """Lấy format selector cho độ phân giải"""
        return cls.FORMAT_SELECTORS.get(resolution, cls.FORMAT_SELECTORS["1080p"])

# Tạo instance global để sử dụng trong toàn bộ ứng dụng
config = Config()