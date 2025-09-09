#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test với link Xiaohongshu thật để kiểm tra tính năng
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaohongshu_downloader import XiaohongshuDownloader
from config import config

def test_with_sample_urls():
    """Test với một số URL mẫu"""
    print("=== Test với URL mẫu ===")
    
    downloader = XiaohongshuDownloader()
    
    # Một số URL mẫu để test (có thể không hoạt động do bảo mật)
    sample_urls = [
        "https://www.xiaohongshu.com/explore/65596bce000000001f02ee94",  # URL từ log
        "https://www.xiaohongshu.com/discovery/item/123456789",
        "https://xhslink.com/abc123"
    ]
    
    print("\n📝 Hướng dẫn sử dụng:")
    print("1. Mở ứng dụng Xiaohongshu trên điện thoại hoặc web")
    print("2. Tìm video bạn muốn tải")
    print("3. Nhấn nút 'Chia sẻ' (Share)")
    print("4. Chọn 'Sao chép liên kết' (Copy Link)")
    print("5. Dán link vào ứng dụng này")
    
    print("\n⚠️  Lưu ý quan trọng:")
    print("- Chỉ có thể tải video/ảnh công khai")
    print("- Không thể tải nội dung riêng tư hoặc bị hạn chế")
    print("- Link phải là link gốc từ Xiaohongshu, không phải link rút gọn")
    print("- Một số video có thể bị bảo vệ bởi DRM")
    
    print("\n🔍 Test validation URL:")
    for i, url in enumerate(sample_urls, 1):
        is_valid = downloader.is_xiaohongshu_url(url)
        status = "✅ Hợp lệ" if is_valid else "❌ Không hợp lệ"
        print(f"  {i}. {url}")
        print(f"     {status}")
        
        if is_valid:
            note_id = downloader.extract_note_id(url)
            print(f"     Note ID: {note_id}")
    
    print("\n💡 Các định dạng URL được hỗ trợ:")
    supported_formats = [
        "https://www.xiaohongshu.com/explore/[note_id]",
        "https://xiaohongshu.com/explore/[note_id]",
        "https://www.xiaohongshu.com/discovery/item/[note_id]",
        "https://xhslink.com/[short_id]",
        "https://rednote.com/note/[note_id]"
    ]
    
    for format_url in supported_formats:
        print(f"  ✅ {format_url}")

def test_error_handling():
    """Test xử lý lỗi"""
    print("\n=== Test xử lý lỗi ===")
    
    downloader = XiaohongshuDownloader()
    
    # Test với URL không hợp lệ
    invalid_urls = [
        "https://youtube.com/watch?v=test",
        "https://google.com",
        "invalid_url",
        ""
    ]
    
    print("\n🚫 Test URL không hợp lệ:")
    for url in invalid_urls:
        is_valid = downloader.is_xiaohongshu_url(url)
        print(f"  URL: '{url}' -> {'❌ Không hợp lệ' if not is_valid else '✅ Hợp lệ'}")
    
    # Test với note ID không tồn tại
    print("\n🔍 Test note ID không tồn tại:")
    fake_note_id = "fake123456789"
    note_info = downloader.get_note_info(fake_note_id)
    if note_info is None:
        print(f"  ✅ Xử lý đúng note ID không tồn tại: {fake_note_id}")
    else:
        print(f"  ❌ Không xử lý đúng note ID không tồn tại: {fake_note_id}")

def show_troubleshooting_guide():
    """Hiển thị hướng dẫn khắc phục sự cố"""
    print("\n=== 🛠️  Hướng dẫn khắc phục sự cố ===")
    
    print("\n❓ Nếu không tải được video:")
    print("\n1. 🔗 Kiểm tra link:")
    print("   - Đảm bảo link là từ Xiaohongshu chính thức")
    print("   - Link phải bắt đầu bằng https://www.xiaohongshu.com hoặc https://xhslink.com")
    print("   - Thử mở link trên trình duyệt để kiểm tra")
    
    print("\n2. 🔒 Kiểm tra quyền truy cập:")
    print("   - Video phải là công khai (không riêng tư)")
    print("   - Tài khoản đăng video không bị khóa")
    print("   - Video không bị hạn chế theo khu vực")
    
    print("\n3. 🌐 Kiểm tra kết nối mạng:")
    print("   - Đảm bảo có kết nối internet ổn định")
    print("   - Thử tắt VPN nếu đang sử dụng")
    print("   - Kiểm tra firewall không chặn ứng dụng")
    
    print("\n4. 🔄 Thử lại:")
    print("   - Đợi vài phút rồi thử lại")
    print("   - Restart ứng dụng")
    print("   - Thử với video khác")
    
    print("\n📋 Các lỗi thường gặp:")
    error_solutions = {
        "HTTP 500": "Server Xiaohongshu gặp lỗi hoặc video đã bị xóa",
        "HTTP 403": "Không có quyền truy cập, video có thể bị hạn chế",
        "HTTP 404": "Không tìm thấy video, link có thể đã bị xóa",
        "Không thể trích xuất ID": "Link không đúng định dạng Xiaohongshu",
        "Không thể lấy thông tin video": "Video không công khai hoặc bị bảo vệ"
    }
    
    for error, solution in error_solutions.items():
        print(f"   • {error}: {solution}")

def main():
    """Chạy tất cả các test và hướng dẫn"""
    print("🧪 Test tính năng Xiaohongshu Downloader")
    print("=" * 50)
    
    try:
        test_with_sample_urls()
        test_error_handling()
        show_troubleshooting_guide()
        
        print("\n" + "=" * 50)
        print("✅ Test hoàn thành!")
        print("\n🚀 Để sử dụng ứng dụng:")
        print("   1. Chạy: python main.py")
        print("   2. Chuyển sang tab 'Xiaohongsu & Vbeef'")
        print("   3. Dán link Xiaohongshu vào ô nhập")
        print("   4. Nhấn 'Download'")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)