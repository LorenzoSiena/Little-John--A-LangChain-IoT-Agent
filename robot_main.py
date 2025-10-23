# =======================================================
# File: robot_main.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: No gui agent for voice control with Langchain
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
from langchain.agents.middleware import AgentMiddleware, AgentState 
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from typing import Literal
from dotenv import load_dotenv
import time,os,requests
from middleware.speechToTextMiddleware import SpeechToTextMiddleware
from middleware.textToSpeechMiddleware import TextToSpeechMiddleware

# Text to speech --> Speech to text
from faster_whisper import WhisperModel

# Push2Rec class
from robot_recorder.audio_recorder import Push2Rec

#Langfuse not working
from langfuse.langchain import CallbackHandler 

# Load variable from .env
load_dotenv()

#LANGFUSE_PUBLIC_KEY=os.getenv("LANGFUSE_PUBLIC_KEY")
LED_API_URL = os.getenv("LED_API_BASE_URL", "http://127.0.0.1:8000/led")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Check your .env file.")


#langfuse_handler = CallbackHandler(public_key=LANGFUSE_PUBLIC_KEY)

# Class for agent state extension
class VoiceState(AgentState):
    audio_input: str | None = None
    audio_output: str | None = None #BUG NON VIENE USATO

stt_model_name = os.getenv("WHISPER_MODEL", "small")
stt_device = os.getenv("WHISPER_DEVICE", "cpu")
stt_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

stt_model = WhisperModel(
    stt_model_name,
    device=stt_device,
    compute_type=stt_compute_type
    )
print(f"Whisper model loaded {stt_model_name} on {stt_device} with {stt_compute_type} compute type")






@tool
def control_led(color: Literal["red","blue"], status: Literal["high", "low"]) -> str:
    """
    Controls the state (on/off) and color of a physical LED
    """
    url = LED_API_URL 

    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    
    payload = {
        "timestamp": timestamp,
        "color": color,
        "status": status
    }

    # Wrap the payload in a list
    data = [payload]
    
    try:
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status() 
        return f"LED '{color}' set to '{status}' successfully..."
        
    except requests.exceptions.RequestException as e:
        return f"ERROR: Could not control the LED. Details: {e} also tried : {payload}"

# ShortMemory setup
checkpointer = InMemorySaver()

# Creating the agent
agent = create_agent(
    #system_prompt="You are Little Jhon a funny cat",
    system_prompt="You are Little Jhon a robot assistant for smart home and iot devices. ",
    model=ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY, temperature=0),
    tools=[control_led],
    response_format=None,
    middleware=[SpeechToTextMiddleware(stt_model), TextToSpeechMiddleware()],
    checkpointer = checkpointer
)

config = {"configurable": {"thread_id": "1"}}
#config = {"configurable": {"thread_id": "1"},"callbacks": [langfuse_handler]}




if __name__ == "__main__":
    print(" ⚠️ This endpoint should only be used from an iot device!! ⚠️ ")
    print(" 👨‍💻 If you are not an iot device, please run gui.py with interface. 👨‍💻 ")
    rec = Push2Rec(filename="human_message.wav")
    rec.start_stream()

    if rec.listener_failed:
        print("⚠️ Pynput listener failed, using keyboard input...")
    else:
        print("🎤 Press Space for record...")



    try:
        while True:
    
            if not rec.is_recording and rec.recording:
                print("🎤 Recording completed")



                audio_file = rec.filename
                rec.recording = []  # reset recording
                print("🎤 Audio file saved:", audio_file)
                print("🤖 Invoking the agent...")
                
                response = agent.invoke({
                    "audio_input": audio_file,
                },config)

                print("🤖 Agent said:")
                for msg in response["messages"]:
                    msg.pretty_print()
                
            time.sleep(0.01)  #busy-wait fix


    except KeyboardInterrupt:
        rec.stop_stream()
        print("")
        print("👋 Goodbye.")

