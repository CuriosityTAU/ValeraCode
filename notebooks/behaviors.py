from queue import PriorityQueue
from global_definitions import *
import threading
import time

from movement import *
from visemes import *

print("Setting behaviors ...")

# there are output channels
# each behavior takes over some of the channels
# each behavior is set a thread to start
# if a new behavior comes, but uses an already occupied output channel, it needs to wait for it to end .join
# for a new behavior, even if only one of its channels is occupied it needs to wait

output_channels = {o : None for o in output_channel_names}

# Create a priority queue instance
behavior_queue = PriorityQueue()
running_behaviors = {}
behavior_history = []

def convert_behavior_to_thread(full_behavior_list, s):
    print("Running behavior: ", s)
    stop_event = threading.Event()

    if "type" in s:
        if "audio_movement" in s["type"]:
            add_behavior(base_priority, {
                "name": "movement",
                "channels": motor_parts,
                "thread": threading.Thread(target=movement_thread, args=(s['movement'], stop_event, s["stop"]))
            })
            add_behavior(base_priority, {
                "name": "face",
                "channels": ["Mouth"],
                "thread": threading.Thread(target=visemes_thread,args=(s['audio'], stop_event, s["stop"], 
                                                                      full_behavior_list['robot_name']))
            })
            add_behavior(base_priority, {
                "name": "audio",
                "channels": "audio",
                "thread": threading.Thread(target=audio_file_thread, args=(s['audio'], stop_event, s["stop"]))
            })
        elif "movement_only" in s["type"]:
            add_behavior(base_priority, {
                "name": "movement",
                "channels": motor_parts,
                "thread": threading.Thread(target=movement_thread, args=(s['movement'], stop_event, s["stop"]))
            })
        elif "audio_face" in s["type"]:
            add_behavior(base_priority, {
                "name": "face",
                "channels": ["Mouth"],
                "thread": threading.Thread(target=visemes_thread,args=(s['audio'], stop_event, s["stop"], 
                                                                      full_behavior_list['robot_name']))
            })
            add_behavior(base_priority, {
                "name": "audio",
                "channels": "audio",
                "thread": threading.Thread(target=audio_file_thread, args=(s['audio'], stop_event, s["stop"]))
            })
        add_behavior(base_priority, {
            "name": "wait",
            "channels": output_channel_names,
            "thread": None
        })
        if s['next'] in full_behavior_list:
            convert_behavior_to_thread(full_behavior_list, full_behavior_list[s['next']])
        else:
            print("ERROR:", full_behavior_list.keys())
    elif "condition" in s:
        if "waitfor" in s["condition"]:
            add_behavior(base_priority, {
                "name": s["condition"],
                "channels": s["perception"],
                "thread": threading.Thread(target=waitfor, args=(s))
            })
    elif "the_start" in s:
        convert_behavior_to_thread(full_behavior_list, full_behavior_list[s["next"]])
    elif "the_end" in s:
        add_behavior(base_priority, {
            "name": "the_end",
            "channels": output_channel_names,
            "thread": None
        })
        
def thread_behavior(full_behavior_list, behavior_name):
    convert_behavior_to_thread(full_behavior_list, full_behavior_list[behavior_name])

def add_behavior(priority, behavior_):
    # behavior_ = {name, channels, thread}
    behavior_queue.put((priority, len(behavior_history), behavior_))
    behavior_history.append(behavior_["name"])

def run_behavior(behavior_):
    for o in behavior_["channels"]:
        output_channels[o] = behavior_["name"]
    running_behaviors[behavior_["name"]] = behavior_["thread"]
    running_behaviors[behavior_["name"]].start()


def manage_behaviors():
    while True:
        # print("behaviors, manage_behaviors", behavior_queue.qsize())
        behavior_to_run = behavior_queue.get()[-1]
        # print("behaviors, manage_behaviors, behavior_to_run", behavior_to_run)
        if behavior_to_run:
            behavior_queue.task_done()
    
            # check if channels to run are occupied
            overlapping_behavior = None
            overlapping_channel = None
            for o in behavior_to_run["channels"]:
                if o in output_channels:
                    if output_channels[o] is not None:
                        overlapping_behavior = output_channels[o]
                        overlapping_channel = o
                        break
            # print("behaviors, manage_behaviors, overlapping_behavior", overlapping_behavior)
    
            if overlapping_behavior is not None and overlapping_behavior in running_behaviors:
                # wait for the overlapping behavior to end
                # print("behaviors, manage_behaviors, waiting for ", overlapping_behavior, " to finish")
                running_behaviors[overlapping_behavior].join()
                
            if behavior_to_run["thread"]:
                run_behavior(behavior_to_run)
            elif behavior_to_run["name"] == "the_end":
                break

            # remove ended behaviors
            dead_behaviors = []
            for rb_name, rb in running_behaviors.items():
                if not rb.is_alive():
                    dead_behaviors.append(rb_name)
            for db in dead_behaviors:
                del running_behaviors[db]
                output_channels[db] = None
                # print('Behaviors, removing ', db)

        else:
            print('behaviors:', 'no behaviors in queue')
        # time.sleep(1)
    
def start_management():
    management_thread = threading.Thread(target=manage_behaviors, daemon=True)
    management_thread.start()
    return management_thread