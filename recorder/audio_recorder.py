# =======================================================
# File: recorder/audio_recorder.py
# Author: Lorenzo Siena
# Date: October 2025
# Description: A class for audio recording with sounddevice
# License: GNU General Public License v3.0 (GPLv3) 
# =======================================================



import sounddevice as sd
import wave

class AudioRecorder:
    def __init__(self, filename="recording.wav", samplerate=16000, channels=1, dtype="int16"):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.is_recording = False
        self.recording = []
        
    def _callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.recording.append(indata.copy().tobytes())

    def start_recording(self):
        if not self.is_recording:
            print("▶️ Start recording...")
            self.is_recording = True
            self.recording = []

    def stop_recording(self):
        if self.is_recording:
            print("⏹ Stop recording")
            self.is_recording = False
            self._save_file()
            return self.filename
        return None

    def _save_file(self):
        audio_bytes = b''.join(self.recording)
        with wave.open(self.filename, "wb") as f:
            f.setnchannels(self.channels)
            f.setsampwidth(2 if self.dtype=="int16" else 4)
            f.setframerate(self.samplerate)
            f.writeframes(audio_bytes)
        print(f"✅ File saved: {self.filename}")

    def start_stream(self):
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback
        )
        self.stream.start()

    def stop_stream(self):
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()