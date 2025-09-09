#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tính năng Xiaohongshu downloader
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaohongshu_downloader import XiaohongshuDownloader
from config import config

def test_xiaohongshu_url_validation():
    """Test validation URL Xiaohongshu"""
    print("=== Test URL Validation ===")
    
    downloader = XiaohongshuDownloader()
    
    # Test các URL hợp lệ
    valid_urls = [
        "https://www.xiaohongshu.com/explore/123456789",
        "https://xiaohongshu.com/explore/abcdef123",
        "https://www.xiaohongshu.com/discovery/item/123456789",
        "https://xhslink.com/abc123"
    ]
    
    # Test các URL không hợp lệ
    invalid_urls = [
        "https://youtube.com/watch?v=123",
        "https://google.com",
        "not_a_url",
        ""
    ]
    
    print("URL hợp lệ:")
    for url in valid_urls:
        result = downloader.is_xiaohongshu_url(url)
        print(f"  {url}: {result}")
        assert result == True, f"URL {url} should be valid"
    
    print("\nURL không hợp lệ:")
    for url in invalid_urls:
        result = downloader.is_xiaohongshu_url(url)
        print(f"  {url}: {result}")
        assert result == False, f"URL {url} should be invalid"
    
    print("✅ Test URL validation thành công!\n")

def test_note_id_extraction():
    """Test trích xuất note ID từ URL"""
    print("=== Test Note ID Extraction ===")
    
    downloader = XiaohongshuDownloader()
    
    test_cases = [
        ("https://www.xiaohongshu.com/explore/123456789", "123456789"),
        ("https://xiaohongshu.com/discovery/item/abcdef123", "abcdef123"),
        ("https://xhslink.com/xyz789", "xyz789"),
        ("https://invalid-url.com", None)
    ]
    
    for url, expected in test_cases:
        result = downloader.extract_note_id(url)
        print(f"  {url} -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("✅ Test note ID extraction thành công!\n")

def test_filename_sanitization():
    """Test làm sạch tên file"""
    print("=== Test Filename Sanitization ===")
    
    downloader = XiaohongshuDownloader()
    
    test_cases = [
        ("Video có ký tự đặc biệt: <>/\\|?*", "Video có ký tự đặc biệt"),
        ("Tên file bình thường", "Tên file bình thường"),
        ("File\"với\"dấu\"nháy", "Filevớidấunháy"),
        ("   Tên file có khoảng trắng   ", "Tên file có khoảng trắng")
    ]
    
    for input_name, expected in test_cases:
        result = downloader.sanitize_filename(input_name)
        print(f"  '{input_name}' -> '{result}'")
        assert result == expected, f"Expected '{expected}', got '{result}'"
    
    print("✅ Test filename sanitization thành công!\n")

def test_downloader_initialization():
    """Test khởi tạo downloader"""
    print("=== Test Downloader Initialization ===")
    
    # Test với thư mục mặc định
    downloader1 = XiaohongshuDownloader()
    print(f"  Thư mục mặc định: {downloader1.output_dir}")
    assert downloader1.output_dir.name == "downloads"
    
    # Test với thư mục tùy chỉnh
    custom_dir = "test_xiaohongshu_downloads"
    downloader2 = XiaohongshuDownloader(custom_dir)
    print(f"  Thư mục tùy chỉnh: {downloader2.output_dir}")
    assert downloader2.output_dir.name == custom_dir
    
    # Kiểm tra thư mục đã được tạo
    assert downloader2.output_dir.exists(), "Thư mục output phải được tạo"
    
    print("✅ Test downloader initialization thành công!\n")

def main():
    """Chạy tất cả các test"""
    print("🚀 Bắt đầu test Xiaohongshu Downloader\n")
    
    try:
        test_downloader_initialization()
        test_xiaohongshu_url_validation()
        test_note_id_extraction()
        test_filename_sanitization()
        
        print("🎉 Tất cả test đã pass thành công!")
        print("\n📝 Lưu ý: Để test tải video thực tế, bạn cần:")
        print("   1. URL Xiaohongshu hợp lệ")
        print("   2. Kết nối internet")
        print("   3. Chạy ứng dụng chính (python main.py)")
        
    except Exception as e:
        print(f"❌ Test thất bại: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)