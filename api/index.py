import sys
import os
from pathlib import Path

# Add the project root and src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Set environment variables before importing anything
from dotenv import load_dotenv
load_dotenv()

# Now import FastAPI and other dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the main application
try:
    # Try relative import first
    from src.app import app as fastapi_app
except ImportError:
    try:
        # Try direct import
        import src.app as app_module
        fastapi_app = app_module.app
    except ImportError:
        # Create a minimal fallback app
        fastapi_app = FastAPI(title="JewelryBox.AI Assistant")
        
        @fastapi_app.get("/")
        async def fallback_root():
            return {"error": "Application failed to load", "status": "error"}

# Vercel-compatible app
app = fastapi_app

# Ensure CORS is properly configured for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Vercel
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "JewelryBox AI is running on Vercel",
        "python_path": sys.path[:3],  # Show first 3 paths for debugging
        "working_directory": str(Path.cwd())
    }

# Debug endpoint for troubleshooting imports
@app.get("/api/debug")
async def debug_info():
    return {
        "project_root": str(project_root),
        "src_path": str(src_path),
        "python_path": sys.path[:5],
        "environment": dict(os.environ),
        "files_in_root": [str(f) for f in project_root.iterdir() if f.is_file()][:10]
    } 