"""
TaskFlow - Application Launcher
Starts FastAPI backend with Uvicorn server and serves the full-stack app.
Usage:
    python run.py
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from backend.app.config import settings

def main():
    print("=" * 60)
    print(f"🚀  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print("=" * 60)
    print(f"📍  Frontend & API:     http://localhost:8000/")
    print(f"📚  Swagger Docs:       http://localhost:8000/docs")
    print(f"📖  ReDoc Docs:         http://localhost:8000/redoc")
    print(f"💾  Database:           MySQL (todo-application)")
    print(f"🔑  Demo Credentials:   demo@taskflow.dev / Password123!")
    print("=" * 60)
    print("Press Ctrl+C to stop the server\n")

    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
