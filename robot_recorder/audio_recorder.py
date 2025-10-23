# =======================================================
# File: robot_recorder/audio_recorder.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: A class for audio recording with pynput and sounddevice (only with keyboard and without gui).
# License: MIT 
# =======================================================


import sounddevice as sd
import wave
from pynput import keyboard


class Push2Rec:
    def __init__(self, filename="recording.wav", samplerate=16000, channels=1, dtype="int16"):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.is_recording = False
        self.recording = []
        self.listener_failed = False        
        try:
            self.listener = keyboard.Listener(on_press=self._on_press,
                                             on_release=self._on_release)
            self.listener.start()
        except Exception as e:
            print("⚠️ Impossible to start pynput listener :", e)
            listener_failed = True
            

    def _callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.recording.append(indata.copy().tobytes())

    def _on_press(self, key):
        if key == keyboard.Key.space and not self.is_recording:
            print("▶️ Start recording...")
            self.is_recording = True
            self.recording = []

    def _on_release(self, key):
        if key == keyboard.Key.space and self.is_recording:
            print("⏹ Stop recording")
            self.is_recording = False
            self._save_file()

    def _save_file(self):
        audio_bytes = b''.join(self.recording)
        with wave.open(self.filename, "wb") as f:
            f.setnchannels(self.channels)
            f.setsampwidth(2 if self.dtype=="int16" else 4)
            f.setframerate(self.samplerate)
            f.writeframes(audio_bytes)
        print(f"✅ File saved: {self.filename}")

    def start_stream(self):
        # avvia lo stream audio e ritorna subito
        self.stream = sd.InputStream(samplerate=self.samplerate,
                                     channels=self.channels,
                                     dtype=self.dtype,
                                     callback=self._callback)
        self.stream.start()

    def stop_stream(self):
        self.stream.stop()
        self.stream.close()
        self.listener.stop()
