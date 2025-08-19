import os
import re
import logging
from typing import Optional
from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 
api_key = "AIzaSyAAsnySExNNzKZfA2rHUrtlFxoba0hnzgw"
@dataclass
class VideoInfo:
    video_id: str
    video_url: str
    chunks_count: int

class YouTubeRAGError(Exception):
    pass

class YouTubeRAGSystem:
    URL_PATTERNS = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)'
    ]
    
    PROMPT_TEMPLATE = """Answer based only on the YouTube transcript context below.
    If insufficient context, say "I don't know".

    Context: {context}
    Question: {question}
    Answer:"""

    def __init__(self, google_api_key: str):
        
        
  
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001',google_api_key=api_key)
        self.llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.2,google_api_key = api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.prompt = PromptTemplate(template=self.PROMPT_TEMPLATE, input_variables=['context', 'question'])
        
        self.current_video_id: Optional[str] = None
        self.vector_store = None
        self.retriever = None

    def extract_video_id(self, url_or_id: str) -> str:
        if not url_or_id:
            raise YouTubeRAGError("URL or video ID cannot be empty")
        
        url_or_id = url_or_id.strip()
        if len(url_or_id) == 11 and url_or_id.isalnum():
            return url_or_id
        
        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        raise YouTubeRAGError(f"Could not extract video ID from: {url_or_id}")

    def get_transcript(self, video_id: str) -> str:
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id)
            return " ".join([x.text for x in transcript])
        
        except TranscriptsDisabled:
            raise YouTubeRAGError(f"Transcripts disabled for video {video_id}")
        except NoTranscriptFound:
            raise YouTubeRAGError(f"No transcript found for video {video_id}")
        except Exception as e:
            raise YouTubeRAGError(f"Error fetching transcript: {e}")

    def process_video(self, video_url_or_id: str) -> bool:
        video_id = self.extract_video_id(video_url_or_id)
        if self.current_video_id == video_id:
            return True

        transcript = self.get_transcript(video_id)
        chunks = self.text_splitter.create_documents([transcript])
        
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        self.current_video_id = video_id
        
        logger.info(f"Processed video {video_id} with {len(chunks)} chunks")
        return True

    def query(self, question: str) -> str:
        if not question.strip():
            raise YouTubeRAGError("Question cannot be empty")
        
        if not self.retriever:
            return "No video processed. Please process a video first."
        
        docs = self.retriever.invoke(question.strip())
        context = "\n\n".join(doc.page_content for doc in docs)
        formatted_prompt = self.prompt.format(context=context, question=question.strip())
        response = self.llm.invoke(formatted_prompt)
        return response.content if hasattr(response, 'content') else str(response)

    def get_video_info(self) -> Optional[VideoInfo]:
        if not self.current_video_id:
            return None
        
        chunks_count = len(self.vector_store.index_to_docstore_id) if self.vector_store else 0
        return VideoInfo(
            video_id=self.current_video_id,
            video_url=f"https://www.youtube.com/watch?v={self.current_video_id}",
            chunks_count=chunks_count
        )
