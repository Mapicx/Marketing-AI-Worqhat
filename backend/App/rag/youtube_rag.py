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
API_KEY = "AIzaSyAAsnySExNNzKZfA2rHUrtlFxoba0hnzgw"
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
        # Ensure the Google API key is available to downstream clients
        key = google_api_key or API_KEY
        if key and not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = key

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model='models/embedding-001',
            google_api_key=key
        )
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash',
            temperature=0.2,
            google_api_key=key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.prompt = PromptTemplate(template=self.PROMPT_TEMPLATE, input_variables=['context', 'question'])
        
        self.current_video_id: Optional[str] = None
        self.vector_store = None
        self.retriever = None

    def extract_video_id(self, url_or_id: str) -> str:
        if not url_or_id:
            raise YouTubeRAGError("URL or video ID cannot be empty")

        url_or_id = url_or_id.strip()
        # Accept standard YouTube ID charset (letters, digits, _ and -) with length 11
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
            return url_or_id

        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        raise YouTubeRAGError(f"Could not extract video ID from: {url_or_id}")

    def get_transcript(self, video_id: str) -> str:
        try:
            # First try direct transcript in common English variants
            preferred_langs = ["en", "en-US", "en-GB"]
            try:
                entries = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_langs)
                return " ".join(entry.get("text", "") for entry in entries)
            except NoTranscriptFound:
                # Try listing transcripts and pick any available (manual or generated) prioritizing English
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                # Try manual English first
                for lang in preferred_langs:
                    try:
                        t = transcript_list.find_manually_created_transcript([lang])
                        return " ".join(x.get("text", "") for x in t.fetch())
                    except Exception:
                        continue
                # Try generated English
                try:
                    t = transcript_list.find_generated_transcript(preferred_langs)
                    return " ".join(x.get("text", "") for x in t.fetch())
                except Exception:
                    pass
                # Fallback: take the first available transcript of any language
                for t in transcript_list:
                    try:
                        return " ".join(x.get("text", "") for x in t.fetch())
                    except Exception:
                        continue
                raise NoTranscriptFound("No transcripts available in any language")
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