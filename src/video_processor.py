"""Video processing module for audio extraction and analysis."""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any


class VideoProcessor:
    """Handles video file processing and audio extraction."""
    
    def __init__(self):
        """Initialize video processor."""
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is available."""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found. Install: brew install ffmpeg")
    
    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file (mp4, avi, mov, etc.)
            output_path: Optional output path for audio file
        
        Returns:
            Path to extracted audio file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output path if not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp3")
        
        # Extract audio using ffmpeg
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn",  # No video
            "-acodec", "libmp3lame",  # MP3 codec
            "-q:a", "2",  # Quality
            "-y",  # Overwrite
            output_path
        ]
        
        result = subprocess.run(cmd, 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to extract audio: {result.stderr.decode()}")
        
        return output_path
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video metadata.
        
        Args:
            video_path: Path to video file
        
        Returns:
            Video metadata dict
        """
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"duration": 0, "format": "unknown"}
        
        import json
        data = json.loads(result.stdout)
        
        duration = float(data.get("format", {}).get("duration", 0))
        format_name = data.get("format", {}).get("format_name", "unknown")
        
        return {
            "duration": duration,
            "format": format_name
        }
    
    def process_video_bytes(self, video_bytes: bytes, filename: str = "video.mp4") -> str:
        """
        Process video from bytes and extract audio.
        
        Args:
            video_bytes: Video file bytes
            filename: Original filename
        
        Returns:
            Path to extracted audio file
        """
        # Save to temp file
        suffix = Path(filename).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        try:
            audio_path = self.extract_audio(tmp_path)
            return audio_path
        finally:
            # Cleanup video file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
