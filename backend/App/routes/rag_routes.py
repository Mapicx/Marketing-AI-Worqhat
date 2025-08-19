from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from App.rag.youtube_rag import YouTubeRAGSystem, YouTubeRAGError

router = APIRouter()

# Initialize the RAG system once with Google API Key from env
import os
GOOGLE_API_KEY = os.getenv("AIzaSyAAsnySExNNzKZfA2rHUrtlFxoba0hnzgw")
yt_rag = YouTubeRAGSystem(GOOGLE_API_KEY)

class VideoRequest(BaseModel):
    video_url: str

class QueryRequest(BaseModel):
    question: str

@router.post("/process")
def process_video(req: VideoRequest):
    try:
        yt_rag.process_video(req.video_url)
        info = yt_rag.get_video_info()
        return {"message": "Video processed successfully", "video_info": info.__dict__ if info else None}
    except YouTubeRAGError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/query")
def query_video(req: QueryRequest):
    try:
        answer = yt_rag.query(req.question)
        return {"answer": answer}
    except YouTubeRAGError as e:
        raise HTTPException(status_code=400, detail=str(e))
