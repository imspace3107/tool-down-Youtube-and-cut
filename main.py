#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Video Downloader Desktop App
Ứng dụng desktop tải và cắt video YouTube
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import random
import time
import logging
from datetime import datetime
from pathlib import Path
from config import config

try:
    import yt_dlp
    import ffmpeg
    from tqdm import tqdm
    from video_downloader import VideoDownloader
    from xiaohongshu_downloader import XiaohongshuDownloader
except ImportError as e:
    print(f"Lỗi import thư viện: {e}")
    print("Vui lòng cài đặt các thư viện cần thiết: pip install -r requirements.txt")
    sys.exit(1)

# Cấu hình logging từ config
log_dir = Path(config.LOG_DIR)
log_dir.mkdir(exist_ok=True)
log_file = config.get_log_file_path()

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Thiết lập logging cho main
logger = logging.getLogger(__name__)

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader & Editor")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Biến lưu trữ
        self.download_folder = tk.StringVar(value=config.DEFAULT_OUTPUT_DIR)
        self.video_links = []
        self.downloaded_videos = []
        self.downloader = None
        self.is_downloading = False
        
        # Xiaohongshu downloader
        self.xiaohongshu_downloader = XiaohongshuDownloader(config.XIAOHONGSHU_OUTPUT_DIR)
        self.is_downloading_xiaohongshu = False
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo các widget chính"""
        # Tạo notebook cho tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: YouTube Downloader
        self.youtube_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.youtube_frame, text="YouTube Downloader")
        self.create_youtube_tab()
        
        # Tab 2: Future Features
        self.future_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.future_frame, text="Xiaohongsu & Vbeef")
        self.create_future_tab()
        
    def create_youtube_tab(self):
        """Tạo tab YouTube downloader"""
        # Frame chính
        main_frame = ttk.Frame(self.youtube_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Phần nhập link
        link_frame = ttk.LabelFrame(main_frame, text="Nhập đường link YouTube", padding=10)
        link_frame.pack(fill="x", pady=(0, 10))
        
        # Text area cho nhiều link
        ttk.Label(link_frame, text="Nhập các đường link YouTube (mỗi link một dòng):").pack(anchor="w")
        self.links_text = scrolledtext.ScrolledText(link_frame, height=6, width=70)
        self.links_text.pack(fill="x", pady=(5, 10))
        
        # Buttons cho link
        link_buttons_frame = ttk.Frame(link_frame)
        link_buttons_frame.pack(fill="x")
        
        ttk.Button(link_buttons_frame, text="Xóa Tất Cả", command=self.clear_links).pack(side="left")
        
        # Frame cài đặt
        settings_frame = ttk.LabelFrame(main_frame, text="Cài đặt tải video", padding=10)
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Chọn thư mục lưu
        folder_frame = ttk.Frame(settings_frame)
        folder_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(folder_frame, text="Thư mục lưu:").pack(side="left")
        ttk.Entry(folder_frame, textvariable=self.download_folder, width=50).pack(side="left", padx=(5, 5), fill="x", expand=True)
        ttk.Button(folder_frame, text="Chọn", command=self.select_folder).pack(side="right")
        
        # Cài đặt độ phân giải
        resolution_frame = ttk.Frame(settings_frame)
        resolution_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(resolution_frame, text="Độ phân giải:").pack(side="left")
        self.resolution_var = tk.StringVar(value=config.DEFAULT_RESOLUTION)
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var, 
                                      values=config.RESOLUTION_OPTIONS, state="readonly", width=10)
        resolution_combo.pack(side="left", padx=(5, 0))
        
        # Frame cắt video
        cut_frame = ttk.LabelFrame(main_frame, text="Cài đặt cắt video", padding=10)
        cut_frame.pack(fill="x", pady=(0, 10))
        
        # Checkbox bật/tắt cắt video
        self.enable_cut = tk.BooleanVar(value=False)
        ttk.Checkbutton(cut_frame, text="Bật cắt video ngẫu nhiên", variable=self.enable_cut).pack(anchor="w")
        
        # Cài đặt thời gian cắt
        time_frame = ttk.Frame(cut_frame)
        time_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(time_frame, text="Thời gian tối thiểu (giây):").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.min_time = tk.IntVar(value=config.MIN_CUT_TIME)
        ttk.Spinbox(time_frame, from_=10, to=300, textvariable=self.min_time, width=10).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(time_frame, text="Thời gian tối đa (giây):").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.max_time = tk.IntVar(value=config.MAX_CUT_TIME)
        ttk.Spinbox(time_frame, from_=30, to=600, textvariable=self.max_time, width=10).grid(row=0, column=3)
        
        ttk.Label(time_frame, text="Thời gian tối thiểu cho video ngắn (giây):").grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        self.short_video_time = tk.IntVar(value=config.SHORT_VIDEO_THRESHOLD)
        ttk.Spinbox(time_frame, from_=5, to=60, textvariable=self.short_video_time, width=10).grid(row=1, column=2, pady=(5, 0))
        
        # Frame tiến trình và điều khiển
        control_frame = ttk.LabelFrame(main_frame, text="Điều khiển", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Thanh tiến trình
        ttk.Label(control_frame, text="Tiến trình:").pack(anchor="w")
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(5, 10))
        
        # Label trạng thái
        self.status_label = ttk.Label(control_frame, text="Sẵn sàng")
        self.status_label.pack(anchor="w")
        
        # Buttons điều khiển
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.download_button = ttk.Button(button_frame, text="Bắt Đầu Tải", command=self.start_download)
        self.download_button.pack(side="left", padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Dừng", command=self.stop_download, state="disabled")
        self.stop_button.pack(side="left")
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8)
        self.log_text.pack(fill="both", expand=True)
        
    def create_future_tab(self):
        """Tạo tab Xiaohongshu downloader"""
        # Frame chính
        main_frame = ttk.Frame(self.future_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Xiaohongshu section
        xiaohongsu_frame = ttk.LabelFrame(main_frame, text="Xiaohongshu Video Downloader", padding=20)
        xiaohongsu_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(xiaohongsu_frame, text="✅ Tải video từ Xiaohongshu (Little Red Book)", font=("Arial", 12, "bold")).pack()
        ttk.Label(xiaohongsu_frame, text="Hỗ trợ tải video và hình ảnh chất lượng cao từ Xiaohongshu").pack(pady=(5, 0))
        
        # URL input
        url_frame = ttk.Frame(xiaohongsu_frame)
        url_frame.pack(fill="x", pady=(15, 10))
        
        ttk.Label(url_frame, text="Link Xiaohongshu (mỗi link một dòng):").pack(anchor="w")
        self.xiaohongsu_text = tk.Text(url_frame, height=4, font=("Arial", 10), wrap="word")
        self.xiaohongsu_text.pack(fill="x", pady=(5, 0))
        
        # Scrollbar cho text widget
        scrollbar = ttk.Scrollbar(url_frame, orient="vertical", command=self.xiaohongsu_text.yview)
        self.xiaohongsu_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.xiaohongsu_text.pack(side="left", fill="both", expand=True)
        
        # Buttons frame
        buttons_frame = ttk.Frame(xiaohongsu_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        self.xiaohongsu_download_btn = ttk.Button(buttons_frame, text="Tải Video", command=self.start_xiaohongshu_download)
        self.xiaohongsu_download_btn.pack(side="left", padx=(0, 10))
        
        self.xiaohongsu_clear_btn = ttk.Button(buttons_frame, text="Xóa Link", command=self.clear_xiaohongshu_url)
        self.xiaohongsu_clear_btn.pack(side="left")
        
        # Status and progress
        status_frame = ttk.LabelFrame(main_frame, text="Trạng thái Xiaohongshu", padding=10)
        status_frame.pack(fill="x", pady=(0, 20))
        
        self.xiaohongshu_status_label = ttk.Label(status_frame, text="Sẵn sàng tải video từ Xiaohongshu")
        self.xiaohongshu_status_label.pack(anchor="w")
        
        self.xiaohongshu_progress = ttk.Progressbar(status_frame, mode="indeterminate")
        self.xiaohongshu_progress.pack(fill="x", pady=(10, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Nhật ký Xiaohongshu", padding=10)
        log_frame.pack(fill="both", expand=True)
        
        self.xiaohongshu_log = scrolledtext.ScrolledText(log_frame, height=10, state="disabled")
        self.xiaohongshu_log.pack(fill="both", expand=True)
        
        # Vbeef section (placeholder)
        vbeef_frame = ttk.LabelFrame(main_frame, text="Vbeef Video Downloader", padding=20)
        vbeef_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Label(vbeef_frame, text="🚧 Tính năng đang phát triển", font=("Arial", 12, "bold")).pack()
        ttk.Label(vbeef_frame, text="Sẽ hỗ trợ tải video từ Vbeef ở độ phân giải cao nhất").pack(pady=(5, 0))
        

        
    def clear_links(self):
        """Xóa tất cả links"""
        self.video_links.clear()
        self.links_text.delete("1.0", tk.END)
        self.log("Đã xóa tất cả links")
        
    def select_folder(self):
        """Chọn thư mục lưu file"""
        folder = filedialog.askdirectory(initialdir=self.download_folder.get())
        if folder:
            self.download_folder.set(folder)
            
    def log(self, message):
        """Ghi log"""
        timestamp = time.strftime("%H:%M:%S")
        logger.info(message)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status):
        """Cập nhật trạng thái"""
        self.status_label.config(text=status)
        self.root.update_idletasks()
        
    def update_progress(self, value):
        """Cập nhật thanh tiến trình"""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def start_download(self):
        """Bắt đầu quá trình tải video"""
        try:
            # Đọc links từ textbox
            links_text = self.links_text.get("1.0", tk.END).strip()
            if not links_text:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất một link YouTube")
                return
                
            self.video_links = [link.strip() for link in links_text.split('\n') if link.strip()]
            logger.info(f"Bắt đầu tải {len(self.video_links)} video(s)")
                
            # Disable/Enable buttons
            self.download_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Reset progress
            self.update_progress(0)
            self.update_status("Đang bắt đầu...")
            
            # Start download in separate thread
            self.download_thread = threading.Thread(target=self.download_process, daemon=True)
            self.download_thread.start()
        except Exception as e:
            error_msg = f"Lỗi khi bắt đầu tải: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log(error_msg)
            messagebox.showerror("Lỗi", error_msg)
        
    def stop_download(self):
        """Dừng quá trình tải"""
        self.update_status("Đang dừng...")
        self.is_downloading = False
        if self.downloader:
            self.downloader.stop()
        self.download_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
    def download_process(self):
        """Quá trình tải video chính"""
        try:
            self.is_downloading = True
            
            # Tạo downloader với callbacks
            self.downloader = VideoDownloader(
                progress_callback=self.update_progress,
                log_callback=self.log,
                status_callback=self.update_status
            )
            
            # Lấy cài đặt
            output_dir = self.download_folder.get()
            resolution = self.resolution_var.get()
            enable_cut = self.enable_cut.get()
            min_time = self.min_time.get()
            max_time = self.max_time.get()
            short_video_time = self.short_video_time.get()
            
            # Kiểm tra thư mục
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            self.log(f"Bắt đầu tải {len(self.video_links)} video(s)")
            self.log(f"Thư mục lưu: {output_dir}")
            self.log(f"Độ phân giải: {resolution}")
            
            if enable_cut:
                self.log(f"Cắt video: {min_time}-{max_time}s (ngắn: {short_video_time}s)")
            
            # Xử lý video
            processed_files = self.downloader.process_videos(
                video_urls=self.video_links,
                output_dir=output_dir,
                resolution=resolution,
                enable_cut=enable_cut,
                min_time=min_time,
                max_time=max_time,
                short_video_time=short_video_time
            )
            
            if self.is_downloading:  # Chỉ hiển thị kết quả nếu không bị dừng
                self.downloaded_videos = processed_files
                self.log(f"\n=== KẾT QUẢ ===")
                self.log(f"Đã xử lý thành công: {len(processed_files)} video")
                
                for i, file_path in enumerate(processed_files, 1):
                    file_name = os.path.basename(file_path)
                    file_size = self.get_file_size(file_path)
                    self.log(f"{i}. {file_name} ({file_size})")
                    
                if processed_files:
                    self.log(f"\nTất cả file đã được lưu trong: {output_dir}")
                    
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            self.update_status("Lỗi")
        finally:
            self.is_downloading = False
            self.download_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def clear_xiaohongshu_url(self):
        """Xóa URL Xiaohongshu"""
        self.xiaohongsu_text.delete(1.0, tk.END)
        self.xiaohongshu_log_message("Đã xóa tất cả URL")
    
    def xiaohongshu_log_message(self, message):
        """Ghi log cho Xiaohongshu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.xiaohongshu_log.config(state="normal")
        self.xiaohongshu_log.insert(tk.END, formatted_message)
        self.xiaohongshu_log.see(tk.END)
        self.xiaohongshu_log.config(state="disabled")
        
        # Cập nhật status label
        self.xiaohongshu_status_label.config(text=message)
    
    def start_xiaohongshu_download(self):
        """Bắt đầu tải video từ Xiaohongshu"""
        urls_text = self.xiaohongsu_text.get(1.0, tk.END).strip()
        
        if not urls_text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất một URL Xiaohongshu")
            return
        
        # Tách các URL từ text
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy URL hợp lệ")
            return
        
        # Kiểm tra tất cả URL
        invalid_urls = []
        valid_urls = []
        
        for url in urls:
            if self.xiaohongshu_downloader.is_xiaohongshu_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        if invalid_urls:
            invalid_list = '\n'.join(invalid_urls[:3])  # Hiển thị tối đa 3 URL không hợp lệ
            if len(invalid_urls) > 3:
                invalid_list += f'\n... và {len(invalid_urls) - 3} URL khác'
            messagebox.showerror("Lỗi", f"Các URL không hợp lệ:\n{invalid_list}")
            return
        
        if self.is_downloading_xiaohongshu:
            messagebox.showinfo("Thông báo", "Đang tải video, vui lòng đợi...")
            return
        
        # Bắt đầu tải trong thread riêng
        self.is_downloading_xiaohongshu = True
        self.xiaohongsu_download_btn.config(state="disabled")
        self.xiaohongshu_progress.start()
        
        thread = threading.Thread(target=self.xiaohongshu_download_multiple_process, args=(valid_urls,))
        thread.daemon = True
        thread.start()
    
    def xiaohongshu_download_multiple_process(self, urls):
        """Xử lý tải nhiều video Xiaohongshu trong thread riêng"""
        try:
            total_urls = len(urls)
            self.root.after(0, lambda: self.xiaohongshu_log_message(f"🚀 Bắt đầu tải {total_urls} video từ Xiaohongshu"))
            
            successful_downloads = []
            failed_downloads = []
            
            for i, url in enumerate(urls, 1):
                try:
                    self.root.after(0, lambda i=i, total=total_urls, url=url: 
                                  self.xiaohongshu_log_message(f"[{i}/{total}] Đang tải: {url}"))
                    
                    def progress_callback(message, url=url):
                        self.root.after(0, lambda: self.xiaohongshu_log_message(f"  {message}"))
                    
                    # Tải video
                    result = self.xiaohongshu_downloader.download_video(url, progress_callback)
                    
                    if result['success']:
                        successful_downloads.append({'url': url, 'result': result})
                        self.root.after(0, lambda result=result: 
                                      self.xiaohongshu_log_message(f"  ✅ {result['message']}"))
                    else:
                        failed_downloads.append({'url': url, 'error': result['message']})
                        self.root.after(0, lambda result=result: 
                                      self.xiaohongshu_log_message(f"  ❌ {result['message']}"))
                        
                except Exception as e:
                    error_msg = f"Lỗi khi tải {url}: {str(e)}"
                    failed_downloads.append({'url': url, 'error': error_msg})
                    self.root.after(0, lambda msg=error_msg: self.xiaohongshu_log_message(f"  ❌ {msg}"))
            
            # Tổng kết
            summary_result = {
                'success': len(successful_downloads) > 0,
                'total': total_urls,
                'successful': len(successful_downloads),
                'failed': len(failed_downloads),
                'successful_downloads': successful_downloads,
                'failed_downloads': failed_downloads
            }
            
            # Cập nhật UI trong main thread
            self.root.after(0, lambda: self.xiaohongshu_multiple_download_complete(summary_result))
            
        except Exception as e:
            error_msg = f"Lỗi khi xử lý tải nhiều video: {str(e)}"
            self.root.after(0, lambda: self.xiaohongshu_log_message(error_msg))
            self.root.after(0, lambda: self.xiaohongshu_multiple_download_complete({
                'success': False, 'message': error_msg, 'total': len(urls), 'successful': 0, 'failed': len(urls)
            }))
    
    def xiaohongshu_download_process(self, url):
        """Xử lý tải video Xiaohongshu trong thread riêng (single URL)"""
        try:
            self.xiaohongshu_log_message(f"Bắt đầu tải từ: {url}")
            
            def progress_callback(message):
                self.root.after(0, lambda: self.xiaohongshu_log_message(message))
            
            # Tải video
            result = self.xiaohongshu_downloader.download_video(url, progress_callback)
            
            # Cập nhật UI trong main thread
            self.root.after(0, lambda: self.xiaohongshu_download_complete(result))
            
        except Exception as e:
            error_msg = f"Lỗi khi tải video: {str(e)}"
            self.root.after(0, lambda: self.xiaohongshu_log_message(error_msg))
            self.root.after(0, lambda: self.xiaohongshu_download_complete({'success': False, 'message': error_msg}))
    
    def xiaohongshu_multiple_download_complete(self, summary_result):
        """Xử lý khi tải nhiều video Xiaohongshu hoàn thành"""
        try:
            self.xiaohongshu_progress.stop()
            self.is_downloading_xiaohongshu = False
            self.xiaohongsu_download_btn.config(state="normal")
            
            total = summary_result.get('total', 0)
            successful = summary_result.get('successful', 0)
            failed = summary_result.get('failed', 0)
            
            # Log tổng kết
            self.xiaohongshu_log_message(f"\n📊 === TỔNG KẾT ===")
            self.xiaohongshu_log_message(f"Tổng số URL: {total}")
            self.xiaohongshu_log_message(f"Thành công: {successful}")
            self.xiaohongshu_log_message(f"Thất bại: {failed}")
            
            # Hiển thị chi tiết các file đã tải thành công
            if summary_result.get('successful_downloads'):
                self.xiaohongshu_log_message(f"\n📁 File đã tải thành công:")
                total_files = 0
                for download in summary_result['successful_downloads']:
                    result = download['result']
                    if result.get('files'):
                        for file_path in result['files']:
                            total_files += 1
                            file_name = os.path.basename(file_path)
                            file_size = self.get_file_size(file_path)
                            self.xiaohongshu_log_message(f"  {total_files}. {file_name} ({file_size})")
            
            # Hiển thị lỗi nếu có
            if summary_result.get('failed_downloads'):
                self.xiaohongshu_log_message(f"\n❌ URL thất bại:")
                for i, failed in enumerate(summary_result['failed_downloads'][:5], 1):  # Hiển thị tối đa 5 lỗi
                    self.xiaohongshu_log_message(f"  {i}. {failed['url']}: {failed['error']}")
                if len(summary_result['failed_downloads']) > 5:
                    remaining = len(summary_result['failed_downloads']) - 5
                    self.xiaohongshu_log_message(f"  ... và {remaining} lỗi khác")
            
            # Hiển thị thông báo
            if successful > 0:
                if failed == 0:
                    message = f"🎉 Đã tải thành công tất cả {successful} video!"
                    messagebox.showinfo("Hoàn thành", message)
                else:
                    message = f"⚠️ Đã tải thành công {successful}/{total} video.\nCó {failed} video thất bại."
                    messagebox.showwarning("Hoàn thành một phần", message)
            else:
                message = f"❌ Không thể tải video nào.\nTất cả {total} URL đều thất bại."
                messagebox.showerror("Thất bại", message)
                
        except Exception as e:
            error_msg = f"Lỗi khi xử lý kết quả tổng kết: {str(e)}"
            self.xiaohongshu_log_message(error_msg)
            messagebox.showerror("Lỗi", error_msg)
    
    def xiaohongshu_download_complete(self, result):
        """Xử lý khi tải video Xiaohongshu hoàn thành (single URL)"""
        try:
            self.xiaohongshu_progress.stop()
            self.is_downloading_xiaohongshu = False
            self.xiaohongsu_download_btn.config(state="normal")
            
            if result['success']:
                self.xiaohongshu_log_message(f"✅ {result['message']}")
                if result.get('title'):
                    self.xiaohongshu_log_message(f"Tiêu đề: {result['title']}")
                if result.get('author'):
                    self.xiaohongshu_log_message(f"Tác giả: {result['author']}")
                
                # Hiển thị danh sách file đã tải
                if result.get('files'):
                    self.xiaohongshu_log_message("File đã tải:")
                    for i, file_path in enumerate(result['files'], 1):
                        file_name = os.path.basename(file_path)
                        file_size = self.get_file_size(file_path)
                        self.xiaohongshu_log_message(f"  {i}. {file_name} ({file_size})")
                
                messagebox.showinfo("Thành công", f"Đã tải thành công!\n{result['message']}")
            else:
                self.xiaohongshu_log_message(f"❌ {result['message']}")
                messagebox.showerror("Lỗi", result['message'])
                
        except Exception as e:
            error_msg = f"Lỗi khi xử lý kết quả: {str(e)}"
            self.xiaohongshu_log_message(error_msg)
            messagebox.showerror("Lỗi", error_msg)
            
    def get_file_size(self, file_path):
        """Lấy kích thước file"""
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
        except:
            return "Unknown"

def main():
    """Hàm main"""
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()