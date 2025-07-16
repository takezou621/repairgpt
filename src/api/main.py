"""
FastAPI main application with i18n support
"""

from fastapi import FastAPI
from . import create_app
from .routes import router

# Create FastAPI app with i18n support
app = create_app()

# Include API routes
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "RepairGPT API",
        "version": "1.0.0",
        "docs": "/docs",
        "i18n_support": ["en", "ja"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)