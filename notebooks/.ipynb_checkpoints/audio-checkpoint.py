from gtts import gTTS
from pygame import mixer, time
from playsound import playsound
from io import BytesIO
import librosa
import numpy as np

print("Setting audio ...")

mixer.init()
sample_rate = 0.1

def get_envelope(file, sample=sample_rate, max_length=-1):
    y, sr = librosa.load(file, sr=None)
    if max_length > 0:
        y = y[:sr*max_length]
    envelope = librosa.onset.onset_strength(y=y, sr=sr, hop_length=int(sr * sample))
    envelope = envelope / np.max(envelope)
    return envelope

audio_objects = {}

def update_audio_objects(audio_file):
    audio_objects[audio_file] = {
        "sound": mixer.Sound(audio_file),
        "envelope": get_envelope(audio_file)
    }

def audio_speech(text):
    tts = gTTS(text = text, lang="en", slow=False)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    audio_file(mp3_fp)

def audio_file(file):
    mixer.music.load(file)
    mixer.music.set_volume(1.0)
    mixer.music.play()
    while mixer.music.get_busy():
        time.Clock().tick(10)
    mixer.music.stop()


def audio_speech_thread(text, stop_event, stop_condition):
    tts = gTTS(text = text, lang="en", slow=True)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp)
    mixer.music.play()

    while mixer.music.get_busy():
        time.Clock().tick(10)
        if stop_event.is_set():
            break
    mixer.music.stop()
    
    if "audio" in stop_condition:
        stop_event.set()

def audio_file_thread(file, stop_event, stop_condition):
    print("audio1", file)
    if file not in audio_objects:
        update_audio_objects(file)
        print("audio2")
    sound = audio_objects[file]["sound"]
    
    sound.play()
    print("audio3")

    while mixer.get_busy():
        time.Clock().tick(10)
        if stop_event.is_set():
            break
    sound.stop()
    
    if "audio" in stop_condition:
        stop_event.set()

# audio_file("assets/audio/gesture_wave_both.wav")
# audio_speech("hello my name is valera")