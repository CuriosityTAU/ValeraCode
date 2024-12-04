from character import *
from behaviors import *
import time
from threading import Thread
from perception import *
from follow import *

print("Setting alive mode ...")


def blink():
    blink_sequence = {
        "Eyes": ("blink", [str(i) for i in range(1,8)])
    }
    stop_event = threading.Event()
    t = Thread(target=character_face_thread, args=(blink_sequence, stop_event, None, 0.1))
    return t


def follow_face():
    if len(state['users']) > 0:
        user = state['users'][0]
        if user['face']:
            t = Thread(target=follow_torso, args=(user['face']['norm_center'],))
            return t
    return None


def be_alive():
    # blinking
    while True:
        # blinking
        # if "blink" not in running_behaviors:
        #     add_behavior(base_priority - 1, {
        #         "name": "blink",
        #         "channels": ["Eyes"],
        #         "thread": blink()
        #     })

        # follow face
        if "follow_face" not in running_behaviors:
            follow_face_thread = follow_face()
            if follow_face_thread is not None:
                print('***** face detected and followed *****')
                add_behavior(base_priority - 1, {
                    "name": "follow_face",
                    "channels": ["neck", "torso"],
                    "thread": follow_face_thread
                })
        
        time.sleep(0.1)

def start_alive():
    Thread(target=be_alive, daemon=True).start()