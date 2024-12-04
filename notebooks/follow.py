from movement import *
import time

def follow_torso(norm_x):
    current_torso = current_position['torso']
    delta_torso = 10 * norm_x
    print('Following: current', current_torso, ', Face:', norm_x)
    move_motors({'torso': current_torso + delta_torso})