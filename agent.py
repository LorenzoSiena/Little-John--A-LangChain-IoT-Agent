# =======================================================
# File: agent.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: Agent for voice control with Langchain, has the ability to control a physical LED.
# Requirements: 
#               A Gemini key (also free tier), 
#               Langchain, 
#               Whisper 
#               all the requirements.txt, 
#               a pc with python3 and uv, 
#               a speaker 
#               and a microphone
# License: MIT 
# =======================================================

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import AgentState 
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from typing import Literal
import os, time, requests

# Middleware
from middleware.speechToTextMiddleware import SpeechToTextMiddleware
from middleware.textToSpeechMiddleware import TextToSpeechMiddleware


# =====================
#  INIT ENVIRONMENT
# =====================
load_dotenv()

LED_API_URL = os.getenv("LED_API_BASE_URL", "http://127.0.0.1:8000/led")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Check your .env file.")


# =====================
#  STATE DEFINITION
# =====================
class VoiceState(AgentState):
    audio_input: str | None = None
    audio_output: str | None = None


# =====================
#  TOOLS
# =====================
@tool
def control_led(color: Literal["red", "blue"], status: Literal["high", "low"]) -> str:
    """Controls the state (on/off) and color of a physical LED."""
    url = LED_API_URL
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    payload = [{"timestamp": timestamp, "color": color, "status": status}]
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return f"LED '{color}' set to '{status}' successfully..."
    except requests.exceptions.RequestException as e:
        return f"ERROR: Could not control the LED. Details: {e}"


# =====================
#  STT MODEL
# =====================
def load_stt_model():
    stt_model_name = os.getenv("WHISPER_MODEL", "small")
    stt_device = os.getenv("WHISPER_DEVICE", "cpu")
    stt_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    model = WhisperModel(stt_model_name, device=stt_device, compute_type=stt_compute_type)
    print(f"Whisper model loaded {stt_model_name} on {stt_device} ({stt_compute_type})")
    return model


# =====================
#  AGENT FACTORY
# =====================
def create_voice_agent():
    """Builds and returns the voice-enabled agent instance."""
    stt_model = load_stt_model()
    checkpointer = InMemorySaver()

    agent = create_agent(
        system_prompt="You are Little Jhon, a robot assistant for smart home and IoT devices.",
        model=ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0
        ),
        tools=[control_led],
        middleware=[
            SpeechToTextMiddleware(stt_model),
            TextToSpeechMiddleware()
        ],
        checkpointer=checkpointer
    )

    return agent


# =====================
#  EXPORTS
# =====================
agent = create_voice_agent()
config = {"configurable": {"thread_id": "1"}}

# =====================
#  OPTIONAL ENTRYPOINT
# =====================
if __name__ == "__main__":
    print("✅ Agent ready and loaded.")
