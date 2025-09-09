#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho các cải tiến mới của Xiaohongshu downloader
"""

import sys
import os
from xiaohongshu_downloader import XiaohongshuDownloader

def test_xiaohongshu_downloader():
    print("=== Test Xiaohongshu Downloader với các cải tiến mới ===")
    print()
    
    # Khởi tạo downloader
    downloader = XiaohongshuDownloader()
    
    # Test URLs
    test_urls = [
        "https://www.xiaohongshu.com/explore/65f8a2b5000000001e00c5e4",
        "https://www.xiaohongshu.com/discovery/item/65f8a2b5000000001e00c5e4",
        "https://xhslink.com/abc123"
    ]
    
    print("Các cải tiến mới:")
    print("1. Thêm endpoint POST mới từ thư viện xhs")
    print("2. Thêm web scraping như phương án dự phòng")
    print("3. Cải thiện error handling với thông báo chi tiết")
    print("4. Cập nhật headers để tương thích với API mới")
    print()
    
    for i, url in enumerate(test_urls, 1):
        print(f"Test {i}: {url}")
        
        # Extract note ID
        note_id = downloader.extract_note_id(url)
        if note_id:
            print(f"  ✓ Note ID: {note_id}")
            
            # Test get note info với các endpoint mới
            print("  Đang thử các endpoint mới...")
            note_info = downloader.get_note_info(note_id)
            
            if note_info:
                print(f"  ✓ Thành công lấy thông tin note")
                print(f"  ✓ Type: {note_info.get('type', 'unknown')}")
                if 'title' in note_info:
                    print(f"  ✓ Title: {note_info['title'][:50]}...")
            else:
                print("  ✗ Không thể lấy thông tin note")
        else:
            print("  ✗ Không thể extract note ID")
        
        print()
    
    print("=== Hướng dẫn sử dụng ===")
    print("1. Mở ứng dụng desktop (python main.py)")
    print("2. Chuyển sang tab 'Xiaohongshu'")
    print("3. Dán link Xiaohongshu vào ô text")
    print("4. Chọn thư mục lưu file")
    print("5. Nhấn 'Tải xuống'")
    print()
    print("Lưu ý: Chỉ có thể tải nội dung công khai")
    print("Nếu gặp lỗi 500/403/404, thử link khác")

if __name__ == "__main__":
    test_xiaohongshu_downloader()