"""FastAPI application for the AI pipeline."""

from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from pathlib import Path
import tempfile

# Load .env file
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from .media_pipeline import MediaPipeline


# Request models
class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text content to analyze")
    source: str = Field(default="api", description="Source identifier")


# Initialize app
app = FastAPI(
    title="Akhila AI Pipeline",
    description="AI-powered text analysis pipeline for ingestion, processing, and insights",
    version="1.0.0"
)

# Initialize pipeline
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
AI_MODEL = os.getenv("AI_MODEL", None)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

pipeline = MediaPipeline(
    db_path="data/pipeline.db",
    ai_provider=AI_PROVIDER,
    ai_model=AI_MODEL,
    whisper_model=WHISPER_MODEL
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple web UI."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Akhila AI Pipeline</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            textarea { width: 100%; height: 150px; padding: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: #f8f9fa; padding: 15px; margin-top: 15px; border-radius: 5px; }
            pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🤖 Akhila AI Pipeline</h1>
        <p>Multi-modal AI analysis: Text, Audio, and Video</p>
        
        <div class="section">
            <h2>📝 Text Analysis</h2>
            <textarea id="textInput" placeholder="Enter text to analyze..."></textarea>
            <br><br>
            <input type="text" id="sourceInput" placeholder="Source (optional)" style="width: 200px; padding: 10px;">
            <button onclick="ingestDocument()">Analyze Text</button>
            <div id="ingestResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>🎬 Video/Audio Upload</h2>
            <p>Upload video (MP4, MOV, AVI) or audio (MP3, WAV, M4A) files for transcription and analysis</p>
            <input type="file" id="mediaFile" accept="video/*,audio/*" style="padding: 10px;">
            <br><br>
            <button onclick="uploadMedia()">Upload & Analyze</button>
            <div id="uploadResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>View Document</h2>
            <input type="number" id="docId" placeholder="Document ID" style="width: 200px; padding: 10px;">
            <button onclick="viewDocument()">View</button>
            <div id="viewResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Statistics</h2>
            <button onclick="getStats()">Refresh Stats</button>
            <div id="statsResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>API Documentation</h2>
            <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>
        </div>
        
        <script>
            async function uploadMedia() {
                const fileInput = document.getElementById('mediaFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a file');
                    return;
                }
                
                const div = document.getElementById('uploadResult');
                div.style.display = 'block';
                div.innerHTML = '<p>⏳ Uploading and processing... This may take 30-90 seconds...</p>';
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('source', 'web-upload');
                
                // Determine endpoint based on file type
                const isVideo = file.type.startsWith('video/');
                const endpoint = isVideo ? '/ingest/video' : '/ingest/audio';
                
                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    div.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                } catch (error) {
                    div.innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                }
            }
            
            async function ingestDocument() {
                const text = document.getElementById('textInput').value;
                const source = document.getElementById('sourceInput').value || 'web-ui';
                
                if (!text) {
                    alert('Please enter text');
                    return;
                }
                
                const response = await fetch('/ingest', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text, source})
                });
                
                const result = await response.json();
                const div = document.getElementById('ingestResult');
                div.style.display = 'block';
                div.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            }
            
            async function viewDocument() {
                const docId = document.getElementById('docId').value;
                if (!docId) {
                    alert('Please enter document ID');
                    return;
                }
                
                const response = await fetch(`/documents/${docId}`);
                const result = await response.json();
                const div = document.getElementById('viewResult');
                div.style.display = 'block';
                div.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            }
            
            async function getStats() {
                const response = await fetch('/stats');
                const result = await response.json();
                const div = document.getElementById('statsResult');
                div.style.display = 'block';
                div.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            }
        </script>
    </body>
    </html>
    """


@app.post("/ingest")
async def ingest_document(request: IngestRequest):
    """Ingest and analyze a text document."""
    result = pipeline.ingest(request.text, request.source)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/documents/{document_id}")
async def get_document(document_id: int):
    """Retrieve a document with full analysis."""
    result = pipeline.retrieve(document_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.get("/documents")
async def list_documents(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """List all documents."""
    return pipeline.list_all(limit, offset)


@app.get("/search")
async def search_documents(
    sentiment: Optional[str] = Query(default=None, regex="^(positive|negative|neutral)$"),
    entity_type: Optional[str] = Query(default=None)
):
    """Search documents by filters."""
    return pipeline.search(sentiment, entity_type)


@app.post("/ingest/audio")
async def ingest_audio(file: UploadFile = File(...), source: str = Form(default="audio_upload")):
    """Ingest and analyze an audio file."""
    if not file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename).suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = pipeline.ingest_audio(tmp_path, source)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/ingest/video")
async def ingest_video(file: UploadFile = File(...), source: str = Form(default="video_upload")):
    """Ingest and analyze a video file."""
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename).suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = pipeline.ingest_video(tmp_path, source)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    return pipeline.stats()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = pipeline.stats()
        return {
            "status": "healthy",
            "database": "ok",
            "ai_provider": AI_PROVIDER,
            "ai_model": pipeline.analyzer.model
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {str(e)}")
