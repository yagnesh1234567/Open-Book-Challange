# Quick Start Guide - Akhila AI Pipeline

**Get running in 5 minutes!**


## Prerequisites

- Python 3.11 or higher
- OpenAI API key (or Anthropic/Ollama)
- Terminal/Command line access


## Installation Steps

### 1. Navigate to Project
```bash
cd akhila-ai-pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# For macOS/Linux:
nano .env

# For Windows:
notepad .env

# Add your key:
OPENAI_API_KEY=sk-your-actual-key-here
```

### 5. Test the Pipeline
```bash
python test_pipeline.py
```

Expected output:
```
🚀 Testing Akhila AI Pipeline
✓ Pipeline initialized
✓ Processed successfully (ID: 1)
...
✅ Pipeline test completed successfully!
```

### 6. Start API Server
```bash
python main.py
```

Server starts at: http://localhost:8000

### 7. Open Web UI
Open browser: http://localhost:8000


## Quick Test with cURL

```bash
# Ingest a document
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is an amazing product! Customers love it.",
    "source": "test"
  }'

# View the result (use document_id from above)
curl http://localhost:8000/documents/1

# Get statistics
curl http://localhost:8000/stats
```


## Alternative: Use Ollama (Free, Local)

If you don't have an API key:

```bash
# Install Ollama: https://ollama.ai
# Pull model
ollama pull llama3

# Edit .env
AI_PROVIDER=ollama
AI_MODEL=llama3
# No API key needed!

# Run test
python test_pipeline.py
```


## Troubleshooting

### "OPENAI_API_KEY not set"
- Check `.env` file exists
- Verify API key is correct
- Restart terminal after editing `.env`

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Change port in .env
PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

### "Database locked"
```bash
# Remove database and restart
rm data/pipeline.db
python test_pipeline.py
```


## Next Steps

1. ✅ Read `README.md` for full documentation
2. ✅ Check `docs/TECHNICAL_APPROACH.md` for architecture
3. ✅ View `docs/SAMPLE_OUTPUTS.md` for examples
4. ✅ Explore API docs: http://localhost:8000/docs


## Support

- Check logs in terminal output
- Verify Python version: `python --version`
- Ensure virtual environment is activated
- Review `.env` configuration


**Ready to go!** 🚀
