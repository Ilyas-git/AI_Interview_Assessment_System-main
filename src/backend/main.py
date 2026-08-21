"""
FastAPI Backend for AI Interview Assessment System
Provides endpoints for video analysis with STT and NLP scoring
"""
import os
import tempfile
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stt_service import transcribe_video
from nlp_service import analyze_interview_response

# Initialize FastAPI app
app = FastAPI(
    title="AI Interview Assessment API",
    description="API for analyzing interview responses using Speech-to-Text and NLP",
    version="1.0.0"
)

# Configure CORS for frontend
# In production, set FRONTEND_URL environment variable
frontend_url = os.environ.get("FRONTEND_URL", "*")
allowed_origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "AI Interview Assessment API",
        "version": "1.0.0",
        "endpoints": {
            "/api/health": "Health check",
            "/api/analyze": "POST - Analyze video interview",
            "/api/transcribe": "POST - Transcribe video only"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


@app.post("/api/transcribe")
async def transcribe_video_endpoint(video: UploadFile = File(...)):
    """
    Transcribe video to text only
    """
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        content = await video.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Transcribe
        result = transcribe_video(temp_path)
        return JSONResponse(content={
            "success": True,
            "transcription": result
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.post("/api/analyze")
async def analyze_interview(video: UploadFile = File(...)):
    """
    Full analysis pipeline: Video → Transcription → NLP Scoring
    """
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        content = await video.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Step 1: Transcribe video
        transcription = transcribe_video(temp_path)
        
        # Step 2: Analyze with NLP
        analysis = analyze_interview_response(transcription["text"])
        
        return JSONResponse(content={
            "success": True,
            "transcription": transcription,
            "analysis": analysis
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
