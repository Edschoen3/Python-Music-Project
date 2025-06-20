import asyncio
import csv
import os
import time
from datetime import datetime
import sounddevice
import numpy as np
import wave
import pyaudio
from shazamio import Shazam
import ssl
import certifi
import aiohttp
import json

AUDIO_FILENAME = "clip.wav"
CSV_FILENAME = "songs.csv" #Change this based on the file you want to save to
RECORD_SECONDS = 10
SAMPLE_RATE = 44100


def record_audio(duration=RECORD_SECONDS, fs=SAMPLE_RATE):
    print(f"[{datetime.now().isoformat()}] Recording: ")
    try:
        device_info = sounddevice.query_devices(None, 'input')
        channels = min(2, int(device_info['max_input_channels']))

        recording = sounddevice.rec(int(duration * fs), samplerate=fs, channels=channels, dtype=np.float32)
        sounddevice.wait()

        audio_data = np.int16(recording * 32767)

        with wave.open(AUDIO_FILENAME, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

        print("Done with recording.")

    except Exception as e:
        print(f"Error recording audio: {str(e)}")
        raise


async def recognize_song(filename):
    print("Finding song: ")
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        shazam = Shazam()
        out = await shazam.recognize(filename)
        track = out.get('track')

        if track:
            song_info = {
                'title': track.get('title', 'Unknown Title'),
                'artist': track.get('subtitle', 'Unknown Artist'),
                'genre': track.get('genres', {}).get('primary', 'Unknown Genre'),
                'release_date': track.get('releasedate', 'Unknown'),
                'album': 'Unknown Album',
                'label': 'Unknown Label',
                'isrc': track.get('isrc', 'Unknown ISRC'),
                'url': track.get('url', 'No URL Available'),
                'key': track.get('key', 'Unknown Key'),
                'shazam_id': track.get('shazamid', 'Unknown Shazam ID')
            }

            # Try to get additional metadata
            sections = track.get('sections', [])
            for section in sections:
                if section.get('type') == 'SONG':
                    song_info['bpm'] = section.get('beatsPerMin', 'Unknown BPM')
                    song_info['key_notes'] = section.get('notes', 'Unknown Key Notes')

                # Look for metadata section
                metadata = section.get('metadata', [])
                for meta in metadata:
                    if 'Album' in meta.get('title', ''):
                        song_info['album'] = meta.get('text', 'Unknown Album')
                    elif 'Label' in meta.get('title', ''):
                        song_info['label'] = meta.get('text', 'Unknown Label')

            if song_info['title'] != 'Unknown Title' or song_info['artist'] != 'Unknown Artist':
                print(f"Recognized: {song_info['title']} - {song_info['artist']}")
                return song_info
            else:
                print("Both title and artist unknown - treating as unrecognized")
                return None
        return None
    except Exception as e:
        print(f"Error recognizing song: {str(e)}")
        return None


def log_to_csv(song_info, csv_filename=CSV_FILENAME):
    try:
        file_exists = os.path.exists(csv_filename)

        with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    "Date",
                    "Title",
                    "Artist",
                    "Genre",
                    "Release Date",
                    "Album",
                    "Label"
                ])

            writer.writerow([
                datetime.now().strftime('%Y-%m-%d'),  # Just the date
                song_info['title'],
                song_info['artist'],
                song_info['genre'],
                song_info['release_date'],
                song_info['album'],
                song_info['label']
            ])
        print("Logged to CSV")

    except Exception as e:
        print(f"Error writing to CSV: {str(e)}")
        raise


async def main_loop():
    print("Starting song listener")
    previous_title = None
    previous_artist = None

    try:
        while True:
            try:
                record_audio()
                if os.path.exists(AUDIO_FILENAME):
                    song_info = await recognize_song(AUDIO_FILENAME)

                    if song_info and (song_info['title'] != previous_title or song_info['artist'] != previous_artist):
                        log_to_csv(song_info)
                        previous_title = song_info['title']
                        previous_artist = song_info['artist']
                    else:
                        print("Skipping song")
                else:
                    print("Audio file was not created successfully")

            except Exception as e:
                print(f"Unexpected error: {str(e)}")

            try:
                if os.path.exists(AUDIO_FILENAME):
                    os.remove(AUDIO_FILENAME)
            except FileNotFoundError:
                pass

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    asyncio.run(main_loop())