from global_definitions import *
from movement import *
from visemes import *
import threading
from fuzzywuzzy import process
import os
from skeleton_to_valera import *
from behaviors import thread_behavior
import json
from perception import *

print("Setting scripts ...")

def find_closest_match(input_string, possibilities):
    best_match = process.extractOne(input_string, possibilities.keys())[0]
    return possibilities[best_match]


def get_possibilities(path, ext='json'):
    file_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            # Append the full path of the file to the list
            if '.' + ext in file:
                file_paths.append(os.path.join(root, file))

    #files = [path + file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and '.' + ext in file]
    possibility_list_ = {}
    for f in file_paths:
        posibility_name = f.split('/')[-1].replace('.' + ext, '')
        if ext == 'json': # movement
            skeletons = json.load(open(f, 'r'))
            possibility_list_[posibility_name] = convert_skeletons_to_sequence(skeletons)
        elif ext in ['wav', 'mp3']:
            possibility_list_[posibility_name] = f
    return possibility_list_


def read_script(file_):
    file_path = file_
    
    base_path = ""
    with open(file_path, 'r') as file:
        file_contents = file.readlines()
    behavior_list = []
    robot_name = "valera"
    for line in file_contents:
        behavior_line = [s.strip() for s in line.split(",")]
        if '#' in behavior_line[0]:
            continue
        if '$' in behavior_line[0]:
            robot_name = behavior_line[1]
            continue
        if '!' in behavior_line[0]:
            base_path = behavior_line[1]
            continue
        behavior_list.append(behavior_line)

    movement_list = get_possibilities(path='assets/movement/' + base_path, ext='json')
    audio_list = get_possibilities(path='assets/audio/' + base_path, ext='wav')

    behaviors_ = {
        'robot_name': robot_name
    }
    for behavior_index, behavior_line in enumerate(behavior_list):
        behavior_name = behavior_line[0]
        behavior_type = behavior_line[1]
        if behavior_type in action_list:
            # name, type, movement, audio, expression, stop, next(optional)
            if len(behavior_line) < 7: # no next
                if behavior_index < len(behavior_list)-1:
                    behavior_next = behavior_list[behavior_index + 1][0]
                else:
                    behavior_next = "TheEnd"
            else:
                behavior_next = behavior_line[6]

            b = {
                "type": [behavior_type],
                "movement": behavior_line[2],
                "audio": behavior_line[3],
                "expression": behavior_line[4],
                "stop": [behavior_line[5]],
                "next": behavior_next
            }
            if "from_video" in b["type"]:
                movement = find_closest_match(b['movement'], movement_list)
                audio = find_closest_match(b['movement'], audio_list)
            elif "only_audio" in b["type"]:
                movement = b['movement']
                audio = find_closest_match(b['audio'], audio_list)
            elif "audio_movement" in b["type"]:
                movement = find_closest_match(b['movement'], movement_list)
                audio = find_closest_match(b['audio'], audio_list)
            elif "audio_face" in b["type"]:
                movement = b['movement']
                audio = find_closest_match(b['audio'], audio_list)
    
            behaviors_[behavior_name] = {
                "type": b["type"],
                "movement": movement,
                "audio": audio,
                "expression": b["expression"],
                "stop": b["stop"],
                "next": b["next"]
            }
            # preload audio
            update_audio_objects(audio)
        elif behavior_type in perception_list:
            #name, condition, perception, value, timeout, next_correct, next_incorrect, next_timeout(optional)
            if len(behavior_line) < 8: # no next
                if behavior_index < len(behavior_list)-1:
                    behavior_next = behavior_list[behavior_index + 1][0]
                else:
                    behavior_next = "TheEnd"
            else:
                behavior_next = behavior_line[7]
            
            behaviors_[behavior_name] = {
                "condition": behavior_line[1],
                "perception": behavior_line[2],
                "value": behavior_line[3],
                "timeout": float(behavior_line[4]),
                "next_correct": behavior_line[5],
                "next_incorrect": behavior_line[6],
                "next_timeout": behavior_next
            }
        else:
            print("PREPROCESS ERROR:", behavior_line)
    
    if "start" not in behaviors_:
        behaviors_["start"] = {
            "the_start": True,
            "next": behavior_list[0][0]
        }

    if "end" not in behaviors_:
        behaviors_["TheEnd"] = {
            "the_end": True
        }
    return behaviors_

def run_script(full_behavior_list):
    thread_behavior(full_behavior_list, "start")