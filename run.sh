#!/bin/bash

# CHAI Chat Interface - Run Script

echo "🚀 Starting CHAI Chat Interface..."

# Install dependencies
echo "Installing dependencies..."
pip install -r frontend/requirements.txt

# Start backend
echo "Starting backend..."
PYTHONPATH=$(pwd)/backend uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "Frontend: http://localhost:8501"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for interrupt
wait