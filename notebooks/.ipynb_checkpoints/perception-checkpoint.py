from queue import Queue
from threading import Thread
from camera import *
import time
from behaviors import add_behavior

print("Setting perception ...")

state = {
    'users': []
}

base_user = {
    'face': None,
    'emotion': None
}

perception_queue = Queue(maxsize=0)

def start_perception():
    Thread(target=process_perception, daemon=True).start()
    Thread(target=start_camera, args=(update_user,), daemon=True).start()

def stop_perception():
    perception_queue.join()
    
def process_perception():
    while True:
        percept = perception_queue.get()
        if len(state['users']) == 0:
            state['users'].append(base_user)
        user = state['users'][0]
        if 'face' in percept:
            if percept['face']['facial_area']['w'] > 0 and percept['face']['facial_area']['w'] < camera_width:
                user['face'] = {
                    'data': percept['face'],
                    'center': percept['face']['facial_area']['x'] + percept['face']['facial_area']['w'] / 2
                }
                user['face']['norm_center'] = (user['face']['center'] - camera_width/2.0) / camera_width

        if 'emotion' in percept:
            print("PERCEPTION, EMOTION:", percept['emotion'])
            user['emotion'] = percept['emotion']

        perception_queue.task_done()
        

def update_user(user_data):
    perception_queue.put(user_data)

def waitfor(info):
    start_time = time.time()
    current_time = time.time() - start_time
    timeout_ = info["timeout"]
    channel_ = info["channel"]
    value_ = inf["value"]
    while current_time < timeout_:
        current_time = time.time() - start_time

        if 'emotion' in channel_:
            if len(state['users']) > 0:
                user = state['users'][0]
                if user[channel_] == value_:
                    break
                


# start_perception()