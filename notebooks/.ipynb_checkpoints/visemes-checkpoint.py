from global_definitions import *
import matplotlib.pyplot as plt
from character import *
from audio import *


print("Setting visemes ...")

def set_viseme(envelope_, character_name="valera"):
    mouth_sequences = characters[character_name]["part_sequence"]["Mouth"]
    for seq in mouth_sequences:
        if "talk" == seq[0]:
            talk_length = len(seq[1])
            break

    talk_sequence =  {
        "Mouth": ("talk", [str(min(talk_length, int(env * talk_length)+1)) for env in envelope_])
    }
    return talk_sequence

def visemes_thread(audio_file, stop_event, stop_condition, character_name="valera"):
    if not audio_file in audio_objects:
        update_audio_objects(audio_file)
    if not "envelop" in audio_objects[audio_file]:
        audio_objects[audio_file]["envelope"] = get_envelope(audio_file)

    envelope = audio_objects[audio_file]["envelope"]
    talk_sequence = set_viseme(envelope, character_name)
    character_face_thread(talk_sequence, stop_event, "face", sample_rate / 2.0, character_name)


# envelope = get_envelope("assets/audio/test.mp3")
# set_viseme(envelope)
# audio_file("assets/audio/test.mp3")

# plt.plot(vol)
# plt.show()
