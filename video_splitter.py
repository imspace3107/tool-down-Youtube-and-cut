import os
import ffmpeg
import logging
from pathlib import Path
from config import config
import math
import random

class VideoSplitter:
    """Split videos into smaller segments using FFmpeg"""
    
    def __init__(self):
        self.output_path = Path(config.OUTPUT_PATH)
        self.segment_duration = config.SEGMENT_DURATION  # 90 seconds (1m30s)
        self.min_last_segment = config.MIN_LAST_SEGMENT_DURATION  # 30 seconds
        self.logger = self._setup_logger()
        
        # Create output directory if it doesn't exist
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger('VideoSplitter')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def get_video_duration(self, video_path):
        """Get video duration in seconds using FFmpeg"""
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception as e:
            self.logger.error(f"Error getting video duration: {e}")
            return None
    
    def calculate_segments(self, duration):
        """Calculate how to split the video into random segments (95-110 seconds)"""
        min_segment = 95  # 1m35s
        max_segment = 110  # 1m50s
        min_last_segment = 70  # Minimum duration for last segment
        
        if duration <= max_segment:
            # Video is shorter than max segment duration, no splitting needed
            return [{'start': 0, 'duration': duration}]
        
        segments = []
        current_time = 0
        
        while current_time < duration:
            remaining_duration = duration - current_time
            
            # Generate random segment duration
            segment_duration = random.randint(min_segment, max_segment)
            
            # Check if this would be the last segment
            if current_time + segment_duration >= duration:
                # This is the last segment
                last_segment_duration = remaining_duration
                
                if last_segment_duration < min_last_segment and segments:
                    # Last segment is too short, merge with previous segment
                    segments[-1]['duration'] += last_segment_duration
                else:
                    # Last segment is long enough or it's the only segment
                    segments.append({
                        'start': current_time,
                        'duration': last_segment_duration
                    })
                break
            else:
                # Regular segment
                segments.append({
                    'start': current_time,
                    'duration': segment_duration
                })
                current_time += segment_duration
        
        return segments
    
    def split_video(self, video_path, video_title, video_id):
        """Split video into segments"""
        try:
            self.logger.info(f"Starting video splitting: {video_path}")
            
            # Get video duration
            duration = self.get_video_duration(video_path)
            if duration is None:
                return {
                    'success': False,
                    'error': 'Could not get video duration'
                }
            
            self.logger.info(f"Video duration: {duration:.2f} seconds")
            
            # Calculate segments
            segments = self.calculate_segments(duration)
            self.logger.info(f"Will create {len(segments)} segments")
            
            # Create output directory for this video
            video_output_dir = self.output_path / self._sanitize_filename(video_title)
            video_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Split video into segments
            output_files = []
            for i, segment in enumerate(segments):
                output_file = self._create_segment(
                    video_path, 
                    segment, 
                    video_output_dir, 
                    video_title, 
                    i + 1
                )
                
                if output_file:
                    output_files.append(output_file)
                else:
                    self.logger.error(f"Failed to create segment {i + 1}")
            
            if output_files:
                self.logger.info(f"Successfully created {len(output_files)} segments")
                return {
                    'success': True,
                    'segments_count': len(output_files),
                    'output_files': output_files,
                    'output_directory': str(video_output_dir)
                }
            else:
                return {
                    'success': False,
                    'error': 'No segments were created successfully'
                }
                
        except Exception as e:
            error_msg = f"Error splitting video: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _create_segment(self, video_path, segment, output_dir, video_title, segment_number):
        """Create a single video segment"""
        try:
            # Create output filename
            safe_title = self._sanitize_filename(video_title)
            output_filename = f"{safe_title}_{segment_number:02d}.mp4"
            output_path = output_dir / output_filename
            
            self.logger.info(
                f"Creating segment {segment_number}: "
                f"start={segment['start']:.2f}s, duration={segment['duration']:.2f}s"
            )
            
            # Use FFmpeg to extract segment
            (
                ffmpeg
                .input(video_path, ss=segment['start'], t=segment['duration'])
                .output(
                    str(output_path),
                    vcodec='copy',  # Copy video codec (faster)
                    acodec='copy',  # Copy audio codec (faster)
                    avoid_negative_ts='make_zero'
                )
                .overwrite_output()
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
            )
            
            # Verify the output file was created
            if output_path.exists() and output_path.stat().st_size > 0:
                self.logger.info(f"Segment {segment_number} created successfully: {output_filename}")
                return {
                    'filename': output_filename,
                    'path': str(output_path),
                    'segment_number': segment_number,
                    'start_time': segment['start'],
                    'duration': segment['duration'],
                    'size': output_path.stat().st_size
                }
            else:
                self.logger.error(f"Segment {segment_number} file was not created or is empty")
                return None
                
        except ffmpeg.Error as e:
            error_msg = f"FFmpeg error creating segment {segment_number}: {e.stderr.decode() if e.stderr else str(e)}"
            self.logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Unexpected error creating segment {segment_number}: {str(e)}"
            self.logger.error(error_msg)
            return None
    
    def _sanitize_filename(self, filename):
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        return filename
    
    def get_video_info_ffmpeg(self, video_path):
        """Get detailed video information using FFmpeg"""
        try:
            probe = ffmpeg.probe(video_path)
            
            video_stream = None
            audio_stream = None
            
            for stream in probe['streams']:
                if stream['codec_type'] == 'video' and video_stream is None:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            info = {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate']),
                'format_name': probe['format']['format_name']
            }
            
            if video_stream:
                info.update({
                    'video_codec': video_stream['codec_name'],
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'fps': eval(video_stream['r_frame_rate']),
                    'video_bitrate': int(video_stream.get('bit_rate', 0))
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream['codec_name'],
                    'sample_rate': int(audio_stream['sample_rate']),
                    'channels': int(audio_stream['channels']),
                    'audio_bitrate': int(audio_stream.get('bit_rate', 0))
                })
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting video info with FFmpeg: {e}")
            return None
    
    def cleanup_original_video(self, video_path):
        """Delete the original video file after successful splitting"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                self.logger.info(f"Deleted original video file: {video_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting original video: {e}")
            return False