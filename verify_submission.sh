#!/bin/bash

# Akhila AI Pipeline - Quick Test Script
# Run this to verify everything works before submission

echo "🚀 Akhila AI Pipeline - Pre-Submission Test"
echo "=============================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python --version 2>&1)
echo "   ✓ $python_version"
echo ""

# Check if virtual environment exists
echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"
else
    echo "   ⚠ Virtual environment not found"
    echo "   Creating virtual environment..."
    python -m venv venv
    echo "   ✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
echo "   ✓ Virtual environment activated"
echo ""

# Install dependencies
echo "4. Installing dependencies..."
pip install -q -r requirements.txt
echo "   ✓ Dependencies installed"
echo ""

# Check .env file
echo "5. Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✓ .env file exists"
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo "   ✓ API key configured"
    else
        echo "   ⚠ API key not configured in .env"
        echo "   Please add your OPENAI_API_KEY to .env file"
    fi
else
    echo "   ⚠ .env file not found"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ⚠ Please edit .env and add your API key"
fi
echo ""

# Check file structure
echo "6. Verifying file structure..."
required_files=(
    "src/database.py"
    "src/ai_analyzer.py"
    "src/pipeline.py"
    "src/api.py"
    "main.py"
    "test_pipeline.py"
    "README.md"
    "requirements.txt"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file (MISSING)"
        all_files_exist=false
    fi
done
echo ""

# Check documentation
echo "7. Verifying documentation..."
doc_files=(
    "docs/TECHNICAL_APPROACH.md"
    "docs/AI_USAGE_LOG.md"
    "docs/SAMPLE_OUTPUTS.md"
    "docs/ARCHITECTURE.md"
)

for file in "${doc_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file (MISSING)"
    fi
done
echo ""

# Security check
echo "8. Security check..."
if grep -r "sk-[a-zA-Z0-9]" src/ main.py test_pipeline.py 2>/dev/null; then
    echo "   ⚠ WARNING: Possible API key found in code!"
else
    echo "   ✓ No hardcoded API keys found"
fi

if [ -f ".env" ] && grep -q ".env" .gitignore; then
    echo "   ✓ .env is in .gitignore"
else
    echo "   ⚠ .env should be in .gitignore"
fi
echo ""

# Summary
echo "=============================================="
echo "Pre-Submission Test Complete!"
echo ""
echo "Next Steps:"
echo "1. If .env needs configuration, add your API key"
echo "2. Run: python test_pipeline.py"
echo "3. Run: python main.py"
echo "4. Test API at http://localhost:8000"
echo "5. Review PRE_SUBMISSION_CHECKLIST.md"
echo "6. Submit to Akhila Labs!"
echo ""
echo "Good luck! 🚀"
