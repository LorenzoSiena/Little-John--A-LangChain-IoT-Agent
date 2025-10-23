# =======================================================
# File: gui.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: Graphical user interface for voice control with Langchain
# Requirements: 
#               pygame, a screen, a speaker and a microphone
# License: GNU General Public License v3.0 (GPLv3) 
# =======================================================



import pygame
import sys
from recorder.audio_recorder import AudioRecorder
from agent import create_voice_agent, config
import threading
import queue

class VoiceAssistantGUI:
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.SCREEN_WIDTH = 400
        self.SCREEN_HEIGHT = 150
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Little Jhon - Voice Assistant")
        
        # Colors
        self.COLOR_GREEN = (0, 200, 0)
        self.COLOR_RED = (200, 0, 0)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_WHITE = (255, 255, 255)
        
        # Font
        self.FONT = pygame.font.Font(None, 36)
        
        # Button
        self.BUTTON_RECT = pygame.Rect(50, 25, 300, 100)
        self.KEY_TO_USE = pygame.K_SPACE
        
        # State
        self.is_recording = False
        self.is_processing = False
        
        # Initialize recorder and agent
        self.recorder = AudioRecorder(filename="human_message.wav")
        self.agent = create_voice_agent()
        
        # Response queue for async processing
        self.response_queue = queue.Queue()
        
    def draw_button(self):
        if self.is_processing:
            color = self.COLOR_RED
            text = "Processing..."
            key_hint = ""
        elif self.is_recording:
            color = self.COLOR_RED
            text = "Recording..."
            key_hint = f"(Release {pygame.key.name(self.KEY_TO_USE).upper()})"
        else:
            color = self.COLOR_GREEN
            text = "Ready"
            key_hint = f"(Press {pygame.key.name(self.KEY_TO_USE).upper()})"

        pygame.draw.rect(self.screen, color, self.BUTTON_RECT, border_radius=10)
        
        text_surface = self.FONT.render(text, True, self.COLOR_WHITE)
        text_rect = text_surface.get_rect(center=self.BUTTON_RECT.center)
        self.screen.blit(text_surface, text_rect)
        
        if key_hint:
            hint_font = pygame.font.Font(None, 24)
            hint_surface = hint_font.render(key_hint.replace("SPACE", "SPAZIO"), True, self.COLOR_BLACK)
            hint_rect = hint_surface.get_rect(center=(self.BUTTON_RECT.centerx, self.BUTTON_RECT.bottom + 10))
            self.screen.blit(hint_surface, hint_rect)

    def process_audio(self, audio_file):
        try:
            response = self.agent.invoke({
                "audio_input": audio_file,
            },config)
            self.response_queue.put(response)
        except Exception as e:
            print(f"Error processing audio: {e}")
        finally:
            self.is_processing = False

    def run(self):
        self.recorder.start_stream()
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.is_processing:
                    if event.type == pygame.KEYDOWN:
                        if event.key == self.KEY_TO_USE and not self.is_recording:
                            self.is_recording = True
                            self.recorder.start_recording()

                    if event.type == pygame.KEYUP:
                        if event.key == self.KEY_TO_USE and self.is_recording:
                            self.is_recording = False
                            audio_file = self.recorder.stop_recording()
                            if audio_file:
                                self.is_processing = True
                                thread = threading.Thread(
                                    target=self.process_audio,
                                    args=(audio_file,)
                                )
                                thread.start()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.BUTTON_RECT.collidepoint(event.pos) and not self.is_recording:
                            self.is_recording = True
                            self.recorder.start_recording()

                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.is_recording:
                            self.is_recording = False
                            audio_file = self.recorder.stop_recording()
                            if audio_file:
                                self.is_processing = True
                                thread = threading.Thread(
                                    target=self.process_audio,
                                    args=(audio_file,)
                                )
                                thread.start()

            # Check for agent responses
            try:
                while True:
                    response = self.response_queue.get_nowait()
                    print("🤖 Agent said:")
                    for msg in response["messages"]:
                        msg.pretty_print()
            except queue.Empty:
                pass

            self.screen.fill(self.COLOR_WHITE)
            self.draw_button()
            pygame.display.flip()
            clock.tick(60)

        self.recorder.stop_stream()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = VoiceAssistantGUI()
    app.run()