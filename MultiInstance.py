import subprocess
import threading
# from OscAudioDmx import audio_files, server
import time

lights = ['python', 'OscAudioDmx.py', "--port", "7777"]
speaker_1 = ['python', 'OscAudioDmx.py', "--port", "5009"]
speaker_2 = ['python', 'OscAudioDmx.py', "--port", "5009"]


commands = [lights, speaker_1,speaker_2]
subprocess
for c in commands:
    subprocess.Popen(c)

