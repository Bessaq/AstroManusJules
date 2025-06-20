@echo off
REM Startup script for the Astrological API on Windows

echo Starting Astrological API server...

REM Activate virtual environment if one is used (common practice)
REM Adjust the path to your virtual environment if needed.
REM For example, if your venv is in a folder named 'venv':
REM
REM IF EXIST venv\Scripts\activate.bat (
REM    echo Activating virtual environment from .\venv...
REM    CALL venv\Scripts\activate.bat
REM ) ELSE IF EXIST .venv\Scripts\activate.bat (
REM    echo Activating virtual environment from .\.venv...
REM    CALL .venv\Scripts\activate.bat
REM ) ELSE (
REM    echo Virtual environment not found at .\venv or .\.venv. Assuming dependencies are globally installed or managed otherwise.
REM )

REM Run Uvicorn server
REM --reload will restart the server when code changes (useful for development)
REM You might want to remove --reload for a production-like startup.
echo Running: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo Server stopped.
pause
