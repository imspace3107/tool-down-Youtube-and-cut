import os
import re
import json
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import logging
from typing import Optional, Dict, Any

class XiaohongshuDownloader:
    """
    Class để tải video và hình ảnh từ Xiaohongshu (Little Red Book)
    Sử dụng requests để lấy dữ liệu và tải xuống nội dung
    """
    
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Headers để giả lập trình duyệt
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/',
            'Origin': 'https://www.xiaohongshu.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Thiết lập logging
        self.logger = logging.getLogger(__name__)
    
    def extract_note_id(self, url: str) -> Optional[str]:
        """
        Trích xuất note ID từ URL Xiaohongshu
        """
        try:
            # Pattern cho URL Xiaohongshu
            patterns = [
                r'xiaohongshu\.com/explore/([a-f0-9]+)',
                r'xiaohongshu\.com/discovery/item/([a-f0-9]+)',
                r'xhslink\.com/([a-zA-Z0-9]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            self.logger.warning(f"Không thể trích xuất note ID từ URL: {url}")
            return None
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất note ID: {e}")
            return None
    
    def get_note_info(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết của note từ Xiaohongshu API
        """
        try:
            # Thử nhiều API endpoint khác nhau
            endpoints = [
                # Endpoint web scraping (ưu tiên cao nhất)
                {
                    'url': f'https://www.xiaohongshu.com/explore/{note_id}',
                    'method': 'WEB_SCRAPE'
                },
                # Endpoint cũ (fallback)
                {
                    'url': 'https://www.xiaohongshu.com/api/sns/web/v1/feed',
                    'params': {
                        'source_note_id': note_id,
                        'image_formats': 'jpg,webp,avif',
                        'extra': json.dumps({'need_body_topic': '1'})
                    },
                    'method': 'GET'
                },
                # Endpoint mới từ thư viện xhs
                {
                    'url': 'https://edith.xiaohongshu.com/api/sns/web/v1/feed',
                    'data': {
                        'source_note_id': note_id,
                        'image_formats': ['jpg', 'webp', 'avif'],
                        'extra': {'need_body_topic': '1'}
                    },
                    'method': 'POST'
                }
            ]
            
            for endpoint in endpoints:
                try:
                    if endpoint['method'] == 'POST':
                        response = self.session.post(
                            endpoint['url'], 
                            json=endpoint['data'],
                            headers={
                                **self.headers,
                                'Content-Type': 'application/json'
                            }
                        )
                    elif endpoint['method'] == 'WEB_SCRAPE':
                        # Thử web scraping nếu API thất bại
                        response = self.session.get(
                            endpoint['url'],
                            headers={
                                **self.headers,
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                            }
                        )
                        if response.status_code == 200:
                            # Tìm kiếm dữ liệu JSON trong HTML
                            html_content = response.text
                            import re
                            
                            # Thử nhiều pattern khác nhau
                            patterns = [
                                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                                r'window\.__INITIAL_SSR_STATE__\s*=\s*(\{.*?\});',
                                r'window\.__NUXT__\s*=\s*(\{.*?\});',
                                r'"noteDetailMap":\s*(\{[^}]*"' + re.escape(note_id) + r'"[^}]*\})',
                                r'"video":\s*(\{[^}]*"url"[^}]*\})',
                                r'"imageList":\s*(\[[^\]]*\])'
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, html_content, re.DOTALL)
                                if match:
                                    try:
                                        if 'noteDetailMap' in pattern:
                                            # Tìm note data trực tiếp
                                            note_match = re.search(r'"' + re.escape(note_id) + r'":\s*(\{.*?\}(?=,"[a-f0-9]{24}"|\}))', html_content, re.DOTALL)
                                            if note_match:
                                                note_data = json.loads(note_match.group(1))
                                                self.logger.info(f"Thành công lấy thông tin note từ web scraping (direct): {endpoint['url']}")
                                                return note_data
                                        else:
                                            initial_state = json.loads(match.group(1))
                                            # Tìm note data trong initial state
                                            if 'note' in initial_state and 'noteDetailMap' in initial_state['note']:
                                                note_detail_map = initial_state['note']['noteDetailMap']
                                                if note_id in note_detail_map:
                                                    note_data = note_detail_map[note_id]
                                                    self.logger.info(f"Thành công lấy thông tin note từ web scraping: {endpoint['url']}")
                                                    return note_data
                                            # Thử tìm trong các cấu trúc khác
                                            elif 'data' in initial_state:
                                                data = initial_state['data']
                                                if isinstance(data, dict):
                                                    for key, value in data.items():
                                                        if isinstance(value, dict) and note_id in str(value):
                                                            self.logger.info(f"Tìm thấy note data trong {key}: {endpoint['url']}")
                                                            return value
                                    except (json.JSONDecodeError, KeyError) as e:
                                        self.logger.warning(f"Lỗi parse JSON pattern {pattern}: {e}")
                                        continue
                            
                            # Thử tìm video URL trực tiếp trong HTML
                            video_patterns = [
                                r'"videoUrl":\s*"([^"]+)"',
                                r'"url":\s*"([^"]*\.mp4[^"]*?)"',
                                r'src="([^"]*\.mp4[^"]*?)"'
                            ]
                            
                            for video_pattern in video_patterns:
                                video_match = re.search(video_pattern, html_content)
                                if video_match:
                                    video_url = video_match.group(1)
                                    if video_url and 'mp4' in video_url:
                                        # Tạo note data giả với video URL
                                        fake_note_data = {
                                            'type': 'video',
                                            'title': f'Video {note_id}',
                                            'video': {'url': video_url},
                                            'imageList': []
                                        }
                                        self.logger.info(f"Tìm thấy video URL trực tiếp: {video_url}")
                                        return fake_note_data
                            
                            self.logger.warning(f"Không tìm thấy dữ liệu note trong HTML: {endpoint['url']}")
                        continue
                    else:
                        response = self.session.get(endpoint['url'], params=endpoint['params'])
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data and 'items' in data['data'] and len(data['data']['items']) > 0:
                            self.logger.info(f"Thành công lấy thông tin note từ endpoint: {endpoint['url']}")
                            return data['data']['items'][0]['note_card']
                    elif response.status_code == 500:
                        self.logger.warning(f"Xiaohongshu API trả về lỗi server (500). Link có thể đã bị xóa hoặc không công khai: {note_id}")
                        continue
                    elif response.status_code == 403:
                        self.logger.warning(f"Không có quyền truy cập nội dung này (403). Link có thể bị hạn chế: {note_id}")
                        continue
                    elif response.status_code == 404:
                        self.logger.warning(f"Không tìm thấy nội dung (404). Link có thể đã bị xóa: {note_id}")
                        continue
                    else:
                        self.logger.warning(f"Endpoint {endpoint['url']} trả về status: {response.status_code}")
                        continue
                        
                except Exception as endpoint_error:
                    self.logger.warning(f"Lỗi với endpoint {endpoint['url']}: {endpoint_error}")
                    continue
            
            self.logger.error(f"Tất cả endpoint đều thất bại cho note {note_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy thông tin note: {e}")
            return None
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Làm sạch tên file để tránh ký tự không hợp lệ
        """
        # Loại bỏ ký tự không hợp lệ
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Giới hạn độ dài
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()
    
    def download_file(self, url: str, filepath: Path) -> bool:
        """
        Tải xuống file từ URL
        """
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info(f"Đã tải xuống: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tải file {url}: {e}")
            return False
    
    def download_video(self, url: str, progress_callback=None) -> Dict[str, Any]:
        """
        Tải video từ URL Xiaohongshu
        
        Args:
            url: URL của video Xiaohongshu
            progress_callback: Callback function để báo cáo tiến độ
        
        Returns:
            Dict chứa thông tin kết quả tải xuống
        """
        result = {
            'success': False,
            'message': '',
            'files': [],
            'title': '',
            'author': ''
        }
        
        try:
            if progress_callback:
                progress_callback("Đang trích xuất thông tin...")
            
            # Trích xuất note ID
            note_id = self.extract_note_id(url)
            if not note_id:
                result['message'] = "Không thể trích xuất ID từ URL"
                return result
            
            # Lấy thông tin note
            note_info = self.get_note_info(note_id)
            if not note_info:
                result['message'] = "Không thể lấy thông tin video. Link có thể đã bị xóa, không công khai hoặc bị hạn chế truy cập."
                return result
            
            # Trích xuất thông tin cơ bản
            title = note_info.get('title', f'xiaohongshu_{note_id}')
            author = note_info.get('user', {}).get('nickname', 'unknown')
            
            result['title'] = title
            result['author'] = author
            
            # Tạo thư mục cho video
            safe_title = self.sanitize_filename(f"{title}_{note_id}")
            video_dir = self.output_dir / safe_title
            video_dir.mkdir(exist_ok=True)
            
            if progress_callback:
                progress_callback("Đang tải xuống nội dung...")
            
            downloaded_files = []
            
            # Tải video nếu có
            if 'video' in note_info:
                video_info = note_info['video']
                if 'media' in video_info and 'stream' in video_info['media']:
                    video_url = video_info['media']['stream']['h264'][0]['master_url']
                    video_filename = f"{safe_title}.mp4"
                    video_path = video_dir / video_filename
                    
                    if self.download_file(video_url, video_path):
                        downloaded_files.append(str(video_path))
            
            # Tải hình ảnh nếu có
            if 'image_list' in note_info:
                for i, image_info in enumerate(note_info['image_list']):
                    if 'url_default' in image_info:
                        image_url = image_info['url_default']
                        image_filename = f"{safe_title}_image_{i+1}.jpg"
                        image_path = video_dir / image_filename
                        
                        if self.download_file(image_url, image_path):
                            downloaded_files.append(str(image_path))
            
            if downloaded_files:
                result['success'] = True
                result['files'] = downloaded_files
                result['message'] = f"Đã tải xuống {len(downloaded_files)} file thành công"
            else:
                result['message'] = "Không tìm thấy nội dung để tải xuống"
            
            if progress_callback:
                progress_callback("Hoàn thành!" if result['success'] else "Thất bại!")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tải video: {e}")
            result['message'] = f"Lỗi: {str(e)}"
            if progress_callback:
                progress_callback(f"Lỗi: {str(e)}")
        
        return result
    
    def is_xiaohongshu_url(self, url: str) -> bool:
        """
        Kiểm tra xem URL có phải là URL Xiaohongshu không
        """
        xiaohongshu_domains = [
            'xiaohongshu.com',
            'xhslink.com',
            'rednote.com'
        ]
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            for xhs_domain in xiaohongshu_domains:
                if xhs_domain in domain:
                    return True
            
            return False
            
        except Exception:
            return False