#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tính năng tải nhiều URL Xiaohongshu
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaohongshu_downloader import XiaohongshuDownloader
from config import config

def test_multiple_url_validation():
    """Test validation nhiều URL Xiaohongshu"""
    print("=== Test Multiple URL Validation ===")
    
    downloader = XiaohongshuDownloader()
    
    # Test case: nhiều URL hợp lệ
    valid_urls_text = """https://www.xiaohongshu.com/explore/123456789
https://xiaohongshu.com/explore/abcdef123
https://www.xiaohongshu.com/discovery/item/xyz789
https://xhslink.com/test123"""
    
    urls = [url.strip() for url in valid_urls_text.split('\n') if url.strip()]
    print(f"Tổng số URL: {len(urls)}")
    
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        if downloader.is_xiaohongshu_url(url):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    print(f"URL hợp lệ: {len(valid_urls)}")
    print(f"URL không hợp lệ: {len(invalid_urls)}")
    
    for url in valid_urls:
        print(f"  ✅ {url}")
    
    for url in invalid_urls:
        print(f"  ❌ {url}")
    
    assert len(valid_urls) == 4, f"Expected 4 valid URLs, got {len(valid_urls)}"
    assert len(invalid_urls) == 0, f"Expected 0 invalid URLs, got {len(invalid_urls)}"
    
    print("✅ Test multiple URL validation thành công!\n")

def test_mixed_url_validation():
    """Test validation URL hỗn hợp (hợp lệ và không hợp lệ)"""
    print("=== Test Mixed URL Validation ===")
    
    downloader = XiaohongshuDownloader()
    
    # Test case: URL hỗn hợp
    mixed_urls_text = """https://www.xiaohongshu.com/explore/123456789
https://youtube.com/watch?v=test
https://xiaohongshu.com/discovery/item/abc123
https://google.com
https://xhslink.com/xyz789
invalid_url"""
    
    urls = [url.strip() for url in mixed_urls_text.split('\n') if url.strip()]
    print(f"Tổng số URL: {len(urls)}")
    
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        if downloader.is_xiaohongshu_url(url):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    print(f"URL hợp lệ: {len(valid_urls)}")
    print(f"URL không hợp lệ: {len(invalid_urls)}")
    
    print("\nURL hợp lệ:")
    for url in valid_urls:
        print(f"  ✅ {url}")
    
    print("\nURL không hợp lệ:")
    for url in invalid_urls:
        print(f"  ❌ {url}")
    
    assert len(valid_urls) == 3, f"Expected 3 valid URLs, got {len(valid_urls)}"
    assert len(invalid_urls) == 3, f"Expected 3 invalid URLs, got {len(invalid_urls)}"
    
    print("\n✅ Test mixed URL validation thành công!\n")

def test_empty_and_whitespace():
    """Test xử lý URL trống và khoảng trắng"""
    print("=== Test Empty and Whitespace Handling ===")
    
    downloader = XiaohongshuDownloader()
    
    # Test case: URL với khoảng trắng và dòng trống
    whitespace_urls_text = """  https://www.xiaohongshu.com/explore/123456789  

   
https://xiaohongshu.com/discovery/item/abc123

  https://xhslink.com/xyz789  

"""
    
    urls = [url.strip() for url in whitespace_urls_text.split('\n') if url.strip()]
    print(f"URL sau khi làm sạch: {len(urls)}")
    
    for i, url in enumerate(urls, 1):
        print(f"  {i}. '{url}'")
        assert downloader.is_xiaohongshu_url(url), f"URL {url} should be valid"
    
    assert len(urls) == 3, f"Expected 3 URLs after cleaning, got {len(urls)}"
    
    print("✅ Test empty and whitespace handling thành công!\n")

def test_url_parsing_simulation():
    """Test mô phỏng quá trình parsing URL như trong UI"""
    print("=== Test URL Parsing Simulation ===")
    
    downloader = XiaohongshuDownloader()
    
    # Mô phỏng input từ Text widget
    ui_input = """https://www.xiaohongshu.com/explore/video1
https://xiaohongshu.com/discovery/item/video2
https://youtube.com/watch?v=invalid
https://xhslink.com/video3

https://www.xiaohongshu.com/explore/video4
"""
    
    # Xử lý giống như trong start_xiaohongshu_download
    urls_text = ui_input.strip()
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    print(f"URLs từ UI input: {len(urls)}")
    
    invalid_urls = []
    valid_urls = []
    
    for url in urls:
        if downloader.is_xiaohongshu_url(url):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    print(f"\nKết quả phân tích:")
    print(f"  Tổng URL: {len(urls)}")
    print(f"  Hợp lệ: {len(valid_urls)}")
    print(f"  Không hợp lệ: {len(invalid_urls)}")
    
    if invalid_urls:
        print(f"\nURL không hợp lệ:")
        for url in invalid_urls:
            print(f"  ❌ {url}")
    
    if valid_urls:
        print(f"\nURL hợp lệ:")
        for url in valid_urls:
            print(f"  ✅ {url}")
    
    assert len(valid_urls) == 4, f"Expected 4 valid URLs, got {len(valid_urls)}"
    assert len(invalid_urls) == 1, f"Expected 1 invalid URL, got {len(invalid_urls)}"
    
    print("\n✅ Test URL parsing simulation thành công!\n")

def main():
    """Chạy tất cả các test"""
    print("🚀 Bắt đầu test tính năng tải nhiều URL Xiaohongshu\n")
    
    try:
        test_multiple_url_validation()
        test_mixed_url_validation()
        test_empty_and_whitespace()
        test_url_parsing_simulation()
        
        print("🎉 Tất cả test đã pass thành công!")
        print("\n📝 Tính năng tải nhiều URL đã sẵn sàng:")
        print("   ✅ Hỗ trợ nhập nhiều URL (mỗi dòng một URL)")
        print("   ✅ Validation từng URL riêng biệt")
        print("   ✅ Xử lý URL hỗn hợp (hợp lệ + không hợp lệ)")
        print("   ✅ Làm sạch khoảng trắng và dòng trống")
        print("   ✅ Báo cáo chi tiết kết quả tải")
        print("\n🎯 Để test thực tế, chạy: python main.py")
        
    except Exception as e:
        print(f"❌ Test thất bại: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)