import asyncio
import sounddevice as sd
# from scipy.io.wavfile import write
from shazamio import Shazam
from datetime import datetime
import csv
import time
import os

AUDIO_FILENAME = "clip.wav"
CSV_FILENAME = "songs.csv"
RECORD_SECONDS = 10
SAMPLE_RATE = 44100

def record_audio():
    print(f"[{datetime.now().isoformat()}] Recording: ")
    audio = sd.rec(int(duration * fs), samplerate = fs, channels=2)