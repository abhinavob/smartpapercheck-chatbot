@echo off
echo ==================================================
echo 🚀 Starting Support Chatbot (Backend & Frontend)
echo ==================================================

:: Start backend in a new command window
echo 📂 Starting FastAPI Backend on port 8000...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Start frontend in a new command window
echo 📂 Starting React Frontend on port 5173...
start cmd /k "cd frontend && npm run dev"

echo ==================================================
echo ✅ Both services launched! 
echo - Backend API Docs: http://localhost:8000/docs
echo - Frontend Interface: http://localhost:5173
echo ==================================================
pause
