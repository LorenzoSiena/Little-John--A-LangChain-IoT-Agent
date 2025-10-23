# =======================================================
# File: textToSpeechMiddleware.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: A langchain middleware for text to speech
# Requirements:  
#               pygame
# License: GNU General Public License v3.0 (GPLv3) 
# =======================================================


from langchain.agents.middleware import AgentMiddleware, AgentState 
from typing import Any
from langgraph.runtime import Runtime
import pygame.mixer
from gtts import gTTS
from langchain.messages import AIMessage

# Class for agent state extension
class VoiceState(AgentState):
    audio_input: str | None = None
    audio_output: str | None = None #BUG NON VIENE USATO
# Middleware after model
class TextToSpeechMiddleware(AgentMiddleware):
    
    def after_model(self, state: VoiceState, runtime: Runtime) -> dict[str, Any] | None:

        last_msg = state["messages"][-1] 
        if isinstance(last_msg, AIMessage):
                # If content is a list of blocks
                if isinstance(last_msg.content, list):
                    extracted_text = " ".join(block.get("text", "") for block in last_msg.content)
                else:
                    extracted_text = last_msg.content  # fallback if it's a simple string

                print(f"LLM said: {extracted_text} ")    
                
        if not extracted_text:
            return None
        audio_output=self.text_to_speech(extracted_text)
        print(f"[TTS] Audio generated {audio_output}")
        self.play_audio(audio_output)

    def text_to_speech(self,text: str) -> str:
        #tts = gTTS(text=text, lang="it", slow=False)
        tts = gTTS(text=text, lang="en", slow=False , tld="co.uk")
        #filename = f"voice_agent_response_{int(time.time()*1000)}.mp3"
        filename = f"voice_agent_response.mp3"
        tts.save(filename)
        return filename 
        
    def play_audio(self,filename):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
