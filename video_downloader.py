#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Downloader Module
Module xử lý tải video từ YouTube và các platform khác
"""

import os
import sys
import random
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from config import config
from video_splitter import VideoSplitter

try:
    import yt_dlp
    import ffmpeg
except ImportError as e:
    print(f"Lỗi import: {e}")
    sys.exit(1)

# Thiết lập logging từ config
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.get_log_file_path(), encoding=config.LOG_ENCODING),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self, progress_callback=None, log_callback=None, status_callback=None):
        """
        Khởi tạo VideoDownloader
        
        Args:
            progress_callback: Hàm callback để cập nhật tiến trình (0-100)
            log_callback: Hàm callback để ghi log
            status_callback: Hàm callback để cập nhật trạng thái
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.stop_flag = False
        
    def log(self, message):
        """Ghi log"""
        logger.info(message)
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
            
    def update_progress(self, value):
        """Cập nhật tiến trình"""
        if self.progress_callback:
            self.progress_callback(value)
            
    def update_status(self, status):
        """Cập nhật trạng thái"""
        if self.status_callback:
            self.status_callback(status)
            
    def stop(self):
        """Dừng quá trình tải"""
        self.stop_flag = True
        
    def get_video_info(self, url):
        """
        Lấy thông tin video từ URL
        
        Args:
            url: URL của video
            
        Returns:
            dict: Thông tin video
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive',
                },
                'extractor_retries': 3,
                'fragment_retries': 3,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'formats': info.get('formats', []),
                    'id': info.get('id', ''),
                    'uploader': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            error_msg = f"Lỗi lấy thông tin video {url}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log(error_msg)
            return None
            
    def get_best_format(self, formats, target_resolution):
        """
        Lấy format tốt nhất theo độ phân giải mong muốn
        
        Args:
            formats: Danh sách formats
            target_resolution: Độ phân giải mong muốn (720p, 1080p, 1440p)
            
        Returns:
            dict: Format tốt nhất
        """
        # Chuyển đổi resolution string thành số
        resolution_map = {
            '720p': 720,
            '1080p': 1080,
            '1440p': 1440
        }
        
        target_height = resolution_map.get(target_resolution, 1080)
        
        # Lọc các format video có audio
        video_formats = []
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                height = f.get('height')
                if height and height <= target_height:
                    video_formats.append(f)
                    
        if not video_formats:
            # Nếu không có format phù hợp, lấy format tốt nhất
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            
        if video_formats:
            # Sắp xếp theo độ phân giải giảm dần
            video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
            return video_formats[0]
            
        return None
        
    def download_progress_hook(self, d):
        """Hook để theo dõi tiến trình tải"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.update_progress(percent)
            elif 'total_bytes_estimate' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                self.update_progress(percent)
                
    def download_video(self, url, output_dir, resolution='1080p'):
        """
        Tải video từ URL
        
        Args:
            url: URL video
            output_dir: Thư mục lưu
            resolution: Độ phân giải mong muốn
            
        Returns:
            str: Đường dẫn file đã tải hoặc None nếu lỗi
        """
        try:
            if self.stop_flag:
                return None
                
            self.log(f"Đang tải video: {url}")
            self.update_status("Đang lấy thông tin video...")
            
            # Lấy thông tin video
            info = self.get_video_info(url)
            if not info:
                return None
                
            title = info['title']
            duration = info['duration']
            
            self.log(f"Tiêu đề: {title}")
            self.log(f"Thời lượng: {duration} giây")
            
            # Tạo tên file an toàn
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Giới hạn độ dài
            
            # Cấu hình yt-dlp từ config
            format_selector = self._get_format_selector(resolution)
            self.log(f"Format selector: {format_selector}")
            logger.info(f"Format selector được sử dụng: {format_selector}")
            
            ydl_opts = config.YT_DLP_OPTIONS.copy()
            ydl_opts.update({
                'format': format_selector,
                'outtmpl': os.path.join(output_dir, f'{safe_title}_%(id)s.%(ext)s'),
                'progress_hooks': [self.download_progress_hook],
            })
            
            self.update_status("Đang tải video...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.stop_flag:
                    return None
                
                # Lấy thông tin format trước khi tải
                try:
                    info_dict = ydl.extract_info(url, download=False)
                    if 'format' in info_dict:
                        selected_format = info_dict.get('format', 'Unknown')
                        format_id = info_dict.get('format_id', 'Unknown')
                        resolution_info = f"{info_dict.get('width', '?')}x{info_dict.get('height', '?')}"
                        vbr = info_dict.get('vbr', 'Unknown')
                        vcodec = info_dict.get('vcodec', 'Unknown')
                        
                        self.log(f"Format được chọn: {format_id} - {resolution_info} - {vbr}kbps - {vcodec}")
                        logger.info(f"Chi tiết format: ID={format_id}, Resolution={resolution_info}, VBR={vbr}kbps, Codec={vcodec}")
                except Exception as e:
                    logger.warning(f"Không thể lấy thông tin format: {e}")
                    
                # Tải video
                ydl.download([url])
                
                # Tìm file đã tải
                downloaded_file = self._find_downloaded_file(output_dir, safe_title, info['id'])
                
                if downloaded_file:
                    self.log(f"Đã tải xong: {downloaded_file}")
                    return downloaded_file
                else:
                    self.log("Không tìm thấy file đã tải")
                    return None
                    
        except Exception as e:
            error_msg = f"Lỗi tải video {url}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log(error_msg)
            return None
            
    def _get_format_selector(self, resolution):
        """
        Lấy format selector cho độ phân giải từ config
        
        Args:
            resolution: Độ phân giải mong muốn
            
        Returns:
            str: Format selector string
        """
        return config.get_format_selector(resolution)
        
    def _find_downloaded_file(self, output_dir, title_prefix, video_id):
        """
        Tìm file đã tải trong thư mục
        
        Args:
            output_dir: Thư mục tìm kiếm
            title_prefix: Tiền tố tên file
            video_id: ID video
            
        Returns:
            str: Đường dẫn file hoặc None
        """
        try:
            for file in os.listdir(output_dir):
                if video_id in file and (file.endswith('.mp4') or file.endswith('.mkv') or file.endswith('.webm')):
                    return os.path.join(output_dir, file)
        except Exception:
            pass
        return None
        
    def cut_video_into_segments(self, input_file, output_dir, min_duration, max_duration, short_video_threshold):
        """
        Cắt video thành nhiều đoạn ngắn với thời lượng ngẫu nhiên
        
        Args:
            input_file: File video đầu vào
            output_dir: Thư mục lưu các đoạn video
            min_duration: Thời lượng tối thiểu (giây)
            max_duration: Thời lượng tối đa (giây)
            short_video_threshold: Ngưỡng video ngắn (giây)
            
        Returns:
            list: Danh sách file đã cắt
        """
        try:
            if self.stop_flag:
                return []
                
            # Sử dụng VideoSplitter để cắt video
            splitter = VideoSplitter()
            
            # Lấy tên video từ file path
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            
            # Gọi split_video method
            result = splitter.split_video(
                video_path=input_file,
                video_title=base_name,
                video_id=base_name
            )
            
            if result['success']:
                # Trả về danh sách các file đã cắt
                output_files = [segment['path'] for segment in result['output_files']]
                self.log(f"Đã cắt thành {len(output_files)} đoạn")
                return output_files
            else:
                self.log(f"Lỗi cắt video: {result['error']}")
                return []
            
        except Exception as e:
            error_msg = f"Lỗi cắt video thành nhiều đoạn: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log(error_msg)
            return []

    def cut_video_random(self, input_file, output_file, min_duration, max_duration, short_video_threshold):
        """
        Cắt video ngẫu nhiên
        
        Args:
            input_file: File video đầu vào
            output_file: File video đầu ra
            min_duration: Thời lượng tối thiểu (giây)
            max_duration: Thời lượng tối đa (giây)
            short_video_threshold: Ngưỡng video ngắn (giây)
            
        Returns:
            bool: True nếu thành công
        """
        try:
            if self.stop_flag:
                return False
                
            self.update_status("Đang phân tích video...")
            
            # Lấy thông tin video
            probe = ffmpeg.probe(input_file)
            video_duration = float(probe['streams'][0]['duration'])
            
            self.log(f"Thời lượng video gốc: {video_duration:.2f} giây")
            
            # Xác định thời lượng cắt với buffer an toàn
            buffer_time = 2.0  # Buffer 2 giây
            
            if video_duration <= short_video_threshold:
                # Video ngắn - lấy từ đầu
                start_time = 0
                cut_duration = max(1, min(video_duration - buffer_time, short_video_threshold))
                self.log(f"Video ngắn - cắt từ đầu: {cut_duration:.2f} giây")
            else:
                # Video dài - cắt ngẫu nhiên với logic nối đoạn cuối
                max_cut_duration = min(max_duration, video_duration - buffer_time)
                cut_duration = random.uniform(min_duration, max_cut_duration)
                max_start_time = max(0, video_duration - cut_duration - buffer_time)
                start_time = random.uniform(0, max_start_time)
                
                # Kiểm tra đoạn cuối còn lại
                remaining_time = video_duration - (start_time + cut_duration)
                if remaining_time > 0 and remaining_time < 75:  # Nếu đoạn cuối < 75 giây
                    # Nối đoạn cuối vào video hiện tại
                    cut_duration += remaining_time
                    self.log(f"Nối đoạn cuối {remaining_time:.2f}s vào video - Tổng: {cut_duration:.2f} giây từ {start_time:.2f}")
                else:
                    self.log(f"Cắt ngẫu nhiên: {cut_duration:.2f} giây từ {start_time:.2f}")
                
            self.update_status("Đang cắt video...")
            
            # Sử dụng ffmpeg trực tiếp với tham số chính xác
            try:
                (
                    ffmpeg
                    .input(input_file)
                    .filter('trim', start=start_time, duration=cut_duration)
                    .filter('setpts', 'PTS-STARTPTS')
                    .output(output_file, 
                            vcodec='libx264', 
                            acodec='aac', 
                            preset='medium',
                            crf=18,
                            movflags='faststart')
                    .overwrite_output()
                    .run(quiet=True, capture_stdout=True, capture_stderr=True)
                )
            except ffmpeg.Error as e:
                # Fallback method nếu trim filter không hoạt động
                self.log("Thử phương pháp cắt khác...")
                (
                    ffmpeg
                    .input(input_file, ss=start_time, t=cut_duration)
                    .output(output_file, 
                            vcodec='copy', 
                            acodec='copy')
                    .overwrite_output()
                    .run(quiet=True)
                )
            
            self.log(f"Đã cắt video: {output_file}")
            return True
            
        except Exception as e:
            error_msg = f"Lỗi cắt video: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log(error_msg)
            return False
            
    def process_videos(self, video_urls, output_dir, resolution=None, 
                      enable_cut=False, min_time=None, max_time=None, short_video_time=None):
        """
        Xử lý danh sách video với cấu hình từ config
        
        Args:
            video_urls: Danh sách URL video
            output_dir: Thư mục lưu
            resolution: Độ phân giải (mặc định từ config)
            enable_cut: Có cắt video không
            min_time: Thời gian tối thiểu (mặc định từ config)
            max_time: Thời gian tối đa (mặc định từ config)
            short_video_time: Thời gian cho video ngắn (mặc định từ config)
            
        Returns:
            list: Danh sách file đã xử lý
        """
        # Sử dụng giá trị mặc định từ config nếu không được cung cấp
        if resolution is None:
            resolution = config.DEFAULT_RESOLUTION
        if min_time is None:
            min_time = config.MIN_CUT_TIME
        if max_time is None:
            max_time = config.MAX_CUT_TIME
        if short_video_time is None:
             short_video_time = config.SHORT_VIDEO_THRESHOLD
        processed_files = []
        total_videos = len(video_urls)
        
        try:
            # Tạo thư mục nếu chưa có
            os.makedirs(output_dir, exist_ok=True)
            
            for i, url in enumerate(video_urls):
                if self.stop_flag:
                    break
                    
                self.log(f"\n=== Xử lý video {i+1}/{total_videos} ===")
                
                # Cập nhật tiến trình tổng
                overall_progress = (i / total_videos) * 100
                self.update_progress(overall_progress)
                
                # Tải video
                downloaded_file = self.download_video(url, output_dir, resolution)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    if enable_cut:
                        # Cắt video thành nhiều đoạn
                        base_name = os.path.splitext(os.path.basename(downloaded_file))[0]
                        segments_dir_name = config.get_segments_dir_name(base_name)
                        segments_dir = os.path.join(output_dir, segments_dir_name)
                        os.makedirs(segments_dir, exist_ok=True)
                        
                        cut_files = self.cut_video_into_segments(downloaded_file, segments_dir, 
                                                               min_time, max_time, short_video_time)
                        
                        if cut_files:
                            processed_files.extend(cut_files)
                            self.log(f"Đã cắt thành {len(cut_files)} đoạn video")
                            # Xóa file gốc nếu muốn
                            # os.remove(downloaded_file)
                        else:
                            processed_files.append(downloaded_file)
                    else:
                        processed_files.append(downloaded_file)
                        
            # Hoàn thành
            self.update_progress(100)
            self.update_status("Hoàn thành")
            self.log(f"\n=== Đã xử lý {len(processed_files)} video ===")
            
        except Exception as e:
            self.log(f"Lỗi xử lý video: {str(e)}")
            
        return processed_files