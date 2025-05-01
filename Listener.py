import asyncio
import csv
import os
import time
from datetime import datetime
from scipy.io.wavfile import write
import sounddevice as sd
from shazamio import Shazam

AUDIO_FILENAME = "clip.wav" #Songs saved as
CSV_FILENAME = "songs.csv" #Data saved as
RECORD_SECONDS = 10 #Clip record time
SAMPLE_RATE = 44100 

def record_audio(filename, duration = 10, fs = 44100):
    print(f"[{datetime.now().isoformat()}] Recording: ")
    audio = sd.rec(int(duration * fs), samplerate = fs, channels=2)
    sd.wait()
    write(filename, fs, audio)
    print("Done")

async def recognize_song(filename):
    print("Finding song: ")
    shazam = Shazam()
    out = await shazam.recognize_song(filename)
    track = out.get('track')
    if track:
        title = track.get('title', 'Unknown Title')
        subtitle = track.get('subtitle', 'Unknown Artist')
        print(f"Recognized: {title} - {subtitle}")
        return title, subtitle
    print("No match found.")
    return None, None

def log_to_csv(title, subtitle, csv_filename="songs.csv"):
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode = 'a', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Title", "Artist"])
        writer.writerow([datetime.now().isoformat(), title, subtitle])
    print("Logged to CSV")

async def main_loop():
    print("Starting song listener")
    while True:
        try:
            record_audio(AUDIO_FILENAME, duration = RECORD_SECONDS)
            title, subtitle = await recognize_song(AUDIO_FILENAME)
           # I want to check to make sure that if the song is the same as the song that was played right before that it is not counted in the data
            if title:
                log_to_csv(title, subtitle, CSV_FILENAME)
            else:
                print("Skipping song")
        except Exception as e:
            print("Error: " , e)
        time.sleep(5)

if __name__ == "__main__":
    asyncio.run(main_loop())
