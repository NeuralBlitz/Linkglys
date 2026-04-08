"""Server runner for OpenCode LRS-Agents Cognitive AI Hub."""

from app_factory import create_app
import uvicorn

if __name__ == "__main__":
    app = create_app()
    print("Starting OpenCode LRS-Agents Cognitive AI Hub...")
    print("Server will be available at your Replit URL")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )
