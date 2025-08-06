import gradio as gr
import requests
from pydub import AudioSegment
import os

API_URL = "http://localhost:8000"

def _new_session():
    return None   # sentinel meaning “new session”

def voice_turn(audio_file_path, session_id):
    if audio_file_path is None:
        return "🤖 Please record something first.", session_id

    # Convert to mp3 (Whisper-compatible)
    mp3_path = audio_file_path.replace(".wav", ".mp3")
    audio = AudioSegment.from_file(audio_file_path)
    audio.export(mp3_path, format="mp3")

    with open(mp3_path, "rb") as f:
        resp = requests.post(f"{API_URL}/transcribe", files={"file": f})

    os.remove(mp3_path)

    if resp.status_code != 200:
        return f"❌ Server error: {resp.text}", session_id

    data = resp.json()
    return f"{data['reply']}", data["session_id"]

def text_turn(user_text, session_id):
    """Send text to /chat and return (bot_reply, updated_session_id)"""
    if not user_text.strip():
        return "🤖 You typed nothing.", session_id

    payload = {"session_id": session_id, "text": user_text}
    resp = requests.post(f"{API_URL}/chat", json=payload)

    if resp.status_code != 200:
        return f"❌ Server error: {resp.text}", session_id

    data = resp.json()
    return f"{data['reply']}", data["session_id"]

with gr.Blocks(title="I4Ideas Voice Assistant") as demo:
    gr.Markdown("## 💬 I4Ideas – speak or type to continue the conversation")

    # hidden state that keeps the session_id across turns
    session_state = gr.State(_new_session())

    # ---- Voice section ----
    audio_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙 Speak")
    voice_btn   = gr.Button("Send voice")
    voice_out   = gr.Textbox(label="Voice turn response", interactive=False)

    # ---- Text section ----
    text_input  = gr.Textbox(label="Type message")
    text_btn    = gr.Button("Send text")
    text_out    = gr.Textbox(label="Text turn response", interactive=False)

    # ---- Session id display (read-only) ----
    session_display = gr.Textbox(label="Current session id", interactive=False)

    # ---- Wiring ----
    voice_btn.click(
        fn=voice_turn,
        inputs=[audio_input, session_state],
        outputs=[voice_out, session_state],
    ).then(lambda sid: sid, inputs=[session_state], outputs=[session_display])

    text_btn.click(
        fn=text_turn,
        inputs=[text_input, session_state],
        outputs=[text_out, session_state],
    ).then(lambda sid: sid, inputs=[session_state], outputs=[session_display])

    # clear text box after send
    text_btn.click(lambda: "", outputs=[text_input], queue=False)

if __name__ == "__main__":
    demo.launch()

