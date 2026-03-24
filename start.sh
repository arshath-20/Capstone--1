#!/bin/bash

# Cyber Intrusion Detection System - Startup Script

echo "🛡️  Cyber Intrusion Detection System"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if running in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Not in virtual environment"
    echo "Creating and activating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate || . venv/Scripts/activate
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check if models are trained
if [ ! -f "backend/model/saved_model.pkl" ]; then
    echo ""
    echo "⏳ Training models (first time only)..."
    cd backend/model
    python train.py
    cd ../../
fi

# Start backend in background
echo ""
echo "🚀 Starting FastAPI backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   ✓ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"
cd ../

# Give backend time to start
sleep 3

# Start frontend
echo ""
echo "🎨 Starting Streamlit frontend..."
cd frontend
echo "   ✓ Frontend running on http://localhost:8501"
echo ""
echo "📍 Open http://localhost:8501 in your browser"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
streamlit run app.py --server.port 8501

# Clean up
echo ""
echo "🛑 Shutting down..."
kill $BACKEND_PID 2>/dev/null
echo "✓ Shutdown complete"
