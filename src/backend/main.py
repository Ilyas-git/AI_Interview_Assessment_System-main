"""
FastAPI Backend for AI Interview Assessment System
Provides endpoints for video analysis with Groq Whisper STT and NLP scoring
"""
import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Automatically load .env file if available
for p in [Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env", Path(__file__).resolve().parent.parent.parent / ".env"]:
    if p.exists():
        load_dotenv(dotenv_path=p)
        break

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stt_service import transcribe_video
from nlp_service import analyze_interview_response

app = FastAPI(
    title="AI Interview Assessment API",
    description="API for analyzing interview responses using Speech-to-Text and NLP",
    version="1.0.0"
)

# Configure CORS for frontend
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
@app.get("/api")
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
    groq_configured = bool(os.environ.get("GROQ_API_KEY"))
    return {
        "status": "healthy",
        "message": "API is running",
        "groq_configured": groq_configured
    }


@app.post("/api/transcribe")
async def transcribe_video_endpoint(video: UploadFile = File(...)):
    """
    Transcribe video to text only
    """
    content = await video.read()
    if not content:
        raise HTTPException(status_code=400, detail="File video kosong")

    try:
        result = transcribe_video(content, filename=video.filename or "recording.webm")
        return JSONResponse(content={
            "success": True,
            "transcription": result
        })
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_interview(video: UploadFile = File(...)):
    """
    Full analysis pipeline: Video → Transcription → NLP Scoring
    """
    content = await video.read()
    if not content:
        raise HTTPException(status_code=400, detail="File video kosong")

    try:
        # Step 1: Transcribe video via Groq Whisper Cloud
        transcription = transcribe_video(content, filename=video.filename or "recording.webm")

        # Step 2: Analyze with NLP
        analysis = analyze_interview_response(transcription["text"])

        return JSONResponse(content={
            "success": True,
            "transcription": transcription,
            "analysis": analysis
        })
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
