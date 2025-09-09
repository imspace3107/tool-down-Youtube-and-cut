#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script với link Xiaohongshu thật để kiểm tra tính năng download
"""

import sys
import os
from xiaohongshu_downloader import XiaohongshuDownloader

def test_with_real_links():
    print("=== Test Xiaohongshu Downloader với link thật ===")
    print()
    
    # Khởi tạo downloader
    downloader = XiaohongshuDownloader()
    
    # Hướng dẫn lấy link đúng
    print("Hướng dẫn lấy link Xiaohongshu đúng:")
    print("1. Mở ứng dụng Xiaohongshu trên điện thoại")
    print("2. Tìm video/ảnh công khai (không phải private)")
    print("3. Nhấn 'Chia sẻ' -> 'Sao chép link'")
    print("4. Dán link vào ứng dụng")
    print()
    
    print("Các định dạng link được hỗ trợ:")
    print("- https://www.xiaohongshu.com/explore/[note_id]")
    print("- https://www.xiaohongshu.com/discovery/item/[note_id]")
    print("- https://xhslink.com/[short_id]")
    print()
    
    # Test với link mẫu (có thể không hoạt động)
    test_url = input("Nhập link Xiaohongshu để test (hoặc Enter để bỏ qua): ").strip()
    
    if test_url:
        print(f"\nĐang test với link: {test_url}")
        
        # Extract note ID
        note_id = downloader.extract_note_id(test_url)
        if note_id:
            print(f"✓ Note ID: {note_id}")
            
            # Test get note info
            print("Đang lấy thông tin note...")
            note_info = downloader.get_note_info(note_id)
            
            if note_info:
                print("✓ Thành công lấy thông tin note!")
                print(f"✓ Type: {note_info.get('type', 'unknown')}")
                if 'title' in note_info:
                    print(f"✓ Title: {note_info['title'][:50]}...")
                
                # Test download
                print("\nĐang thử download...")
                result = downloader.download_video(test_url)
                
                if result['success']:
                    print("✓ Download thành công!")
                    print(f"✓ Files: {result['files']}")
                else:
                    print(f"✗ Download thất bại: {result['error']}")
            else:
                print("✗ Không thể lấy thông tin note")
                print("Có thể do:")
                print("- Link đã bị xóa hoặc private")
                print("- Nội dung bị hạn chế")
                print("- Link không đúng định dạng")
        else:
            print("✗ Không thể extract note ID từ link")
    
    print("\n=== Troubleshooting ===")
    print("Nếu không thể tải được:")
    print("1. Kiểm tra link có đúng không")
    print("2. Thử link khác (nội dung công khai)")
    print("3. Kiểm tra kết nối internet")
    print("4. Link có thể đã bị xóa hoặc private")
    print("5. Thử lại sau vài phút")
    print()
    print("Lưu ý: Chỉ có thể tải nội dung công khai!")

if __name__ == "__main__":
    test_with_real_links()