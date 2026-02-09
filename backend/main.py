from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from vision_analyzer import analyze_image
from schemas import AnalysisResponse
import os

# Create FastAPI app
app = FastAPI(
    title="Civic Issue Reporter API",
    description="AI-powered civic infrastructure issue detection",
    version="1.0.0"
)

# Configure CORS - CRITICAL FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Civic Issue Reporter API is running",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_civic_issue(
    file: UploadFile = File(..., description="Image file to analyze"),
    location: str = Form(..., description="Location where the image was taken")
):
    """
    Analyze an uploaded image for civic infrastructure issues
    
    Args:
        file: Image file (JPG, PNG, etc.)
        location: Geographic location of the issue
        
    Returns:
        AnalysisResponse with detected issues and assigned authorities
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate image size (optional, but recommended)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 10MB"
            )
        
        # Analyze the image
        result = analyze_image(image_bytes, location)
        
        # Check if there was an error in analysis
        if "error" in result:
            # Still return the result but log the error
            print(f"Analysis completed with error: {result['error']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_civic_issue endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
