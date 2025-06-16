import asyncio
import csv
import os
import time
from datetime import datetime
import sounddevice
from scipy.io.wavfile import write
import numpy as np
from shazamio import Shazam
###Must import certain packages to run this code###

AUDIO_FILENAME = "clip.wav" #Songs saved as
CSV_FILENAME = "songs.csv" #Data saved as
RECORD_SECONDS = 10 #Clip record time
SAMPLE_RATE = 44100 #The audio rate that the audio is recorded

#Records a section of audio of the environment where music is playing
def record_audio(duration = RECORD_SECONDS, fs = SAMPLE_RATE):
    print(f"[{datetime.now().isoformat()}] Recording: ")
    audio = sounddevice.rec(int(duration * fs), samplerate = fs, channels=2) #Records audio using a sounddevice
    sounddevice.wait()
    write(AUDIO_FILENAME, fs, audio)
    #Create the audio clip
    #Use the wave import to write audio data directly to the wav file
    print("Done with recording.")

async def recognize_song(filename):
    print("Finding song: ")
    shazam = Shazam() #Call Shazam
    out = await shazam.recognize_song(filename)
    track = out.get('track') #Info of the track
    if track:
        #Returns the title if known
        title = track.get('title', 'Unknown Title')
        subtitle = track.get('subtitle', 'Unknown Artist')
        #Checks validity of the song from Shazam
        #Returns if there is one know either artist or title
        if title != 'Unknown Title' or subtitle != 'Unknown Artist':
            print(f"Recognized: {title} - {subtitle}")
            return title, subtitle
        else:
            #Song is unknown
            print("Both title and artist unknown - treating as unrecognized")
            return None, None
    return None, None

def log_to_csv(title, subtitle, csv_filename="songs.csv"):
    #Ensures a path to the file

    try: file_exists = os.path.getsize(csv_filename) ### will throw an exception if the file does not exist
    finally: FileNotFoundError

    with open(csv_filename, mode = 'a', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
       #If the path to the file does not exist, then create a new file with the name
        #And necessary info to start logging songs
        if not file_exists:
            writer.writerow(["Timestamp", "Title", "Artist"])
        #Log the song
        writer.writerow([datetime.now().isoformat(), title, subtitle])
    print("Logged to CSV")

async def main_loop():
    print("Starting song listener")
    previous_title = None
    previous_sub = None
    try:
        while True:
            try:
                record_audio(duration=RECORD_SECONDS,fs=SAMPLE_RATE)
                title, subtitle = await recognize_song(AUDIO_FILENAME)

                # Checks that there is a song to log and is not a duplicate of the last song
                if title and (title != previous_title or subtitle != previous_sub):
                    try:
                        log_to_csv(title, subtitle, CSV_FILENAME)
                        # Update the last song logged to the CSV
                        previous_title = title
                        previous_sub = subtitle
                    except IOError as e:
                        print(f"Error writing to CSV: {e}")
                else:
                    # Skips song if not determined by Shazam or a duplicate
                    print("Skipping song")
            except sounddevice.PortAudioError as e:
                print(f"Audio recording error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

            # Break in recording of the music
            try:
                os.remove(AUDIO_FILENAME)
            except FileNotFoundError:
                pass

            time.sleep(5)
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    asyncio.run(main_loop())
