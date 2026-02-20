"""Audio processing module for transcription and analysis."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any


class AudioProcessor:
    """Handles audio file processing and transcription."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize audio processor.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       base = good quality, fast (74MB)
        """
        self.model_size = model_size
        self.model = None
    
    def _load_model(self):
        """Lazy load Whisper model."""
        if self.model is None:
            import whisper
            self.model = whisper.load_model(self.model_size)
        return self.model
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (mp3, wav, m4a, etc.)
        
        Returns:
            {
                "text": str,
                "language": str,
                "duration": float,
                "segments": list
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        model = self._load_model()
        result = model.transcribe(audio_path)
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "duration": self._get_duration(audio_path),
            "segments": len(result.get("segments", []))
        }
    
    def _get_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert ms to seconds
        except:
            return 0.0
    
    def process_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.mp3") -> Dict[str, Any]:
        """
        Process audio from bytes.
        
        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (for format detection)
        
        Returns:
            Transcription result
        """
        # Save to temp file
        suffix = Path(filename).suffix or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            result = self.transcribe_audio(tmp_path)
            return result
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
