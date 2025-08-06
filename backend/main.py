from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from openai import AzureOpenAI
from langchain_community.chat_models import AzureChatOpenAI
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
import os
from fastapi import BackgroundTasks
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool
from flow import next_turn  # assumed: async def next_turn(sid:str, text:str, llm)

load_dotenv()

app = FastAPI(title="I4Ideas Chatbot")
# -------------------------------------------------
# Azure OpenAI clients
# -------------------------------------------------
# Initialize the langchain_openai client for transcription
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION")
)

# Initialize the langchain_openai client for chat
azure_chat = AzureChatOpenAI(
    openai_api_key=os.getenv("AZURE_API_KEY"),
    openai_api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
)

# -------------------------------------------------
# Pydantic models
# -------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str | None = None
    text: str

class ChatResponse(BaseModel):
    reply: str
    session_id: str

# -------------------------------------------------
# Helper to generate session id
# -------------------------------------------------
def _new_sid() -> str:
    return os.urandom(8).hex()

# -------------------------------------------------
# Endpoints
# -------------------------------------------------
@app.post("/transcribe", response_model=ChatResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Accept any audio container, re-encode to 16 kHz WAV,
    then send to Whisper.
    """
    # 1. Save original bytes
    in_path = tempfile.mktemp(suffix=".wav")
    with open(in_path, "wb") as f:
        f.write(await file.read())

    # 2. Re-encode to 16 kHz mono WAV (avoids container/format issues)
    out_path = tempfile.mktemp(suffix=".wav")
    os.system(
        f"ffmpeg -y -i {in_path} -ar 16000 -ac 1 -f wav {out_path} > /dev/null 2>&1"
    )
    os.remove(in_path)

    try:
        with open(out_path, "rb") as wav:
            transcript = client.audio.transcriptions.create(
                model=os.getenv("AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT"),
                file=wav,
                prompt="Transcribe this audio clearly in English.",
                language="en",
            )
    finally:
        os.remove(out_path)

    user_text = transcript.text.strip()
    sid = _new_sid()
    reply = await next_turn(sid, user_text, azure_chat)
    return ChatResponse(reply=reply, session_id=sid)

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Standard text turn endpoint.
    """
    sid = req.session_id or _new_sid()
    reply = await next_turn(sid, req.text, azure_chat)
    return ChatResponse(reply=reply, session_id=sid)

@app.post("/call_api")
async def call_api(session_id: str = Form(...), user_id: str = Form(...)):
    print(f"Idea submitted — session_id:{session_id}  user_id:{user_id}")
    return {"status": "ok"}