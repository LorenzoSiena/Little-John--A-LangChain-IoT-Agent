# =======================================================
# File: speechToTextMiddleware.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: A langchain middleware for speech to text
# Requirements:  
#               Whisper
# License: MIT 
# =======================================================




from langchain.agents.middleware import AgentMiddleware, AgentState 
from typing import Any
from langchain.messages import HumanMessage
from faster_whisper import WhisperModel
from langgraph.runtime import Runtime

# Class for agent state extension
class VoiceState(AgentState):
    audio_input: str | None = None
    audio_output: str | None = None #BUG NON VIENE USATO

#Middleware before model
class SpeechToTextMiddleware(AgentMiddleware[VoiceState]):
    def __init__(self,stt_model: WhisperModel):
        self.stt_model = stt_model
        super().__init__()

    state_schema = VoiceState

    def before_model(self, state: VoiceState, runtime: Runtime) -> dict[str, Any] | None:
        audio_path = state.get("audio_input", None)
        if audio_path:
            print("[STT] Audio found:", audio_path)
            text = self.speech_to_text(audio_path)
            print("[STT] User said:", text)
            messages = state.get("messages", []) 
            if messages:
                messages.append(HumanMessage(content=text))
            else:
                messages = [HumanMessage(content=text)]
            state["messages"] = messages
            return {"messages": messages, "audio_input": None}  
        else:
            print("[STT] No audio found")
            return None 
        


    def speech_to_text(self,filename: str):
        segments, _ = self.stt_model.transcribe(filename, language="en") # en, it, ecc
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
