pip install sounddevice scipy shazamio
import asyncio
import sounddevice as sd
from scipy.io.wavfile import write
from shazamio import Shazam
from datetime import datetime
import csv
import time
import os
