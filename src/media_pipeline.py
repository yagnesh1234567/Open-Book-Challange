"""Unified media pipeline for text, audio, and video processing."""

import os
from typing import Dict, Any, Optional
from .pipeline import Pipeline
from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor


class MediaPipeline(Pipeline):
    """Extended pipeline supporting text, audio, and video."""
    
    def __init__(self, db_path: str = "data/pipeline.db",
                 ai_provider: str = "openai", ai_model: str = None,
                 whisper_model: str = "base"):
        """
        Initialize media pipeline.
        
        Args:
            db_path: Database path
            ai_provider: AI provider (openai, anthropic, ollama)
            ai_model: AI model name
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        super().__init__(db_path, ai_provider, ai_model)
        self.audio_processor = AudioProcessor(model_size=whisper_model)
        
        # Video processor is optional (requires ffmpeg)
        try:
            self.video_processor = VideoProcessor()
        except RuntimeError as e:
            print(f"⚠️  Video processing disabled: {e}")
            self.video_processor = None
    
    def ingest_text(self, text: str, source: str = "api") -> Dict[str, Any]:
        """Ingest text document (original method)."""
        return self.ingest(text, source)
    
    def ingest_audio(self, audio_path: str, source: str = "audio") -> Dict[str, Any]:
        """
        Ingest audio file: transcribe → analyze.
        
        Args:
            audio_path: Path to audio file
            source: Source identifier
        
        Returns:
            Processing result with transcription and analysis
        """
        try:
            # Transcribe audio
            transcription = self.audio_processor.transcribe_audio(audio_path)
            text = transcription["text"]
            
            if not text or not text.strip():
                return {
                    "status": "error",
                    "message": "No speech detected in audio"
                }
            
            # Analyze transcribed text
            result = self.ingest(text, source)
            
            # Add audio metadata
            if result["status"] == "success":
                result["audio_metadata"] = {
                    "language": transcription["language"],
                    "duration": transcription["duration"],
                    "segments": transcription["segments"]
                }
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Audio processing failed: {str(e)}"
            }
    
    def ingest_video(self, video_path: str, source: str = "video") -> Dict[str, Any]:
        """
        Ingest video file: extract audio → transcribe → analyze.
        
        Args:
            video_path: Path to video file
            source: Source identifier
        
        Returns:
            Processing result with transcription and analysis
        """
        if self.video_processor is None:
            return {
                "status": "error",
                "message": "Video processing not available. Install ffmpeg: brew install ffmpeg"
            }
        
        audio_path = None
        try:
            # Get video info
            video_info = self.video_processor.get_video_info(video_path)
            
            # Extract audio
            audio_path = self.video_processor.extract_audio(video_path)
            
            # Transcribe audio
            transcription = self.audio_processor.transcribe_audio(audio_path)
            text = transcription["text"]
            
            if not text or not text.strip():
                return {
                    "status": "error",
                    "message": "No speech detected in video"
                }
            
            # Analyze transcribed text
            result = self.ingest(text, source)
            
            # Add video metadata
            if result["status"] == "success":
                result["video_metadata"] = {
                    "duration": video_info["duration"],
                    "format": video_info["format"],
                    "language": transcription["language"],
                    "audio_segments": transcription["segments"]
                }
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Video processing failed: {str(e)}"
            }
        
        finally:
            # Cleanup extracted audio
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)
    
    def ingest_file(self, file_path: str, media_type: str = None, 
                   source: str = None) -> Dict[str, Any]:
        """
        Auto-detect and ingest any media file.
        
        Args:
            file_path: Path to file
            media_type: Optional type hint (text, audio, video)
            source: Source identifier
        
        Returns:
            Processing result
        """
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}
        
        # Auto-detect type from extension
        ext = os.path.splitext(file_path)[1].lower()
        
        if media_type is None:
            if ext in ['.txt', '.md', '.doc', '.docx']:
                media_type = 'text'
            elif ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
                media_type = 'audio'
            elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                media_type = 'video'
            else:
                return {"status": "error", "message": f"Unknown file type: {ext}"}
        
        source = source or f"{media_type}_file"
        
        # Process based on type
        if media_type == 'text':
            with open(file_path, 'r') as f:
                text = f.read()
            return self.ingest_text(text, source)
        
        elif media_type == 'audio':
            return self.ingest_audio(file_path, source)
        
        elif media_type == 'video':
            return self.ingest_video(file_path, source)
        
        else:
            return {"status": "error", "message": f"Unsupported media type: {media_type}"}
