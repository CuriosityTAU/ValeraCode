from global_definitions import *
from behaviors import *
from scripts import *
# from perception import *
from alive import *

print("Setting run_valera ...")

global full_behavior_list

def full_run(script=None):
    # first, set the robot up
    move_motors(home_position)

    # start_perception()
    # start_alive()
    management_thread = start_management()

    # run the script
    if script:
        full_behavior_list = read_script(script)
        print("DEBUG: script", script)
        print("DEBUG: script", full_behavior_list)
        characters[full_behavior_list['robot_name']] = initialize_character(characters[full_behavior_list['robot_name']], save=False)
        run_script(full_behavior_list)
    
    # return the robot to home position at the end
    management_thread.join()
    move_motors(home_position)

# full_run("assets/scripts/lesson_02.txt")