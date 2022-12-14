#windows shell prompt: python -m sounddevice get list of devices 
#create ndarry named data with soundfile library
#use sample rate generated by soundfile.read("C:/audio_file_path.wav")
#use sounddevice.play() to playback a song
#set parameter within sd.play(device : int = 8) set the device id after querying 
#set parameter within sd.play(mapping : array_like = [1,2]) starting with one, set the output or input channels for the sound to be played through
#to hard pan an audio data object, set one of the columns of data to zero. This will mute the left or right channel, left being 0, right being 1

#sd.play(data,samplerate=sr,
#            device = 8, mapping = [1,2])

from socketserver import ThreadingUDPServer
import glob
import sounddevice as sd
import soundfile as sf
import argparse
import math
from pythonosc import dispatcher
from pythonosc import osc_server
import random
from stupidArtnet import StupidArtnet
import time
import random
from datetime import datetime

def print_volume_handler(unused_addr, args, volume):
    print("[{0}] ~ {1}".format(args[0], volume))    

def print_compute_handler(unused_addr, args, volume):
  try:
    print(f"[{args[0]}] ~ {args[1](volume)}")
  except ValueError: pass

def play_audio(unused_addr, args, value):
    data = allAudio[0][args[1]]
    sr = allAudio[1][args[1]]
    dev = allAudio[2][args[1]]

    try:
        if value > 0:
            sd.play(data,samplerate=sr,
            device = dev, mapping = [1,2])
        else:
            sd.wait()

    except ValueError: pass

def light_control(unused_addr, args, value):

    universe = 0 									    #Server Specs
    packet_size = 100								# it is not necessary to send whole universe of 255 
    target_ip =  "127.0.0.1"

    a = StupidArtnet(target_ip, universe, packet_size, 30, True, True)           #create artnet server object

    artnetvalue = int(value*255)  #Arbitrary, normalized float rounded to 255 int and set the value
    a.set_single_value(2, artnetvalue)	
    a.start()		
    a.stop()

audio_files = glob.glob("F:\HausZiva\EscapeRoom\SFXMusic\**\*.wav",recursive=True)  #get a list of audio file paths from a folder

device_ids = [5,7] #arbitrary device ids
allAudio = [[],[],[]]
total_files = float(len(audio_files)) #get the total number of audio files

for i, sound in enumerate(audio_files): #create sound object data for each audio file in the given folder #store their respective objects within lists 
    data, samplerate = sf.read(audio_files[i])
    allAudio[0].append(data)
    allAudio[1].append(samplerate)

    if i < total_files *0.5:  #split the audio outputs between two devices, the first have going to one output device, the second half going to another, specified above.
        allAudio[2].append(7)
    if i > total_files *0.5:
        allAudio[2].append(5)  

if __name__ == "__main__":


    parser = argparse.ArgumentParser()    #check CLI args
    parser.add_argument("--ip",
        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=5006, help="The port to listen on")
    parser.add_argument("--start",
        type=int, default=0, help="Start The Server")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()    #dispatch object maps callbacks to messages received

    dispatcher.map("/lightChannel/1", light_control, "Artnet")    #single artnet data traveling over OSC

    for i, file in enumerate(audio_files):    #for each file in the folder, play back the audio file at the index matching the number after /playsound/ address
        address = str(i)
        mapped_address = f"/playsound/{address}"
        dispatcher.map(mapped_address, play_audio,"play", i)

    server = osc_server.ThreadingOSCUDPServer(     #create an osc threaded server
        (args.ip, args.port), dispatcher)
    print(f"Serving on {server.server_address}")
    server.serve_forever()

#--------------------------------------------#unused functions
def random_pan(data):
    rng = random.random()
    if rng <0.5:
        for d in data:
            d[1] = 0
    else:
        for d in data:
            d[0] = 0
    return data