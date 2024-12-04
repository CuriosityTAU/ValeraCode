import numpy as np

print("Setting global definitions ...")

face_parts = ["Eyes", "Nose", "Mouth"]
motor_parts = ['left_shoulder', 'left_elbow', 'right_shoulder', 'right_elbow', 'torso', 'neck']
output_channel_names = face_parts + motor_parts + ['audio']
base_priority = 5

action_list = ["audio_movement", "only_audio", "only_movement", "from_video", "audio_face"]
perception_list = ["waitfor"]

motor_map = {
    'left_shoulder': 4,
    'left_elbow': 2,
    'right_shoulder': 1,
    'right_elbow': 0,
    'torso': 6,
    'neck': 5
}



home_position = {
    'left_shoulder': 500, #up, down
    'left_elbow': 500, #far, close
    'right_shoulder': 200, #down, up
    'right_elbow': 200, #close, far
    'torso': 256, # right, left, middle
    'neck': 425 # right, left, middle
}

motor_bounds = {
    'left_shoulder': (200, 500), #up, down
    'left_elbow': (425, 500), #far, close
    'right_shoulder': (200, 500), #down, up
    'right_elbow': (400, 475), #close, far
    'torso': (156, 356, 256), # right, left, middle
    'neck': (350, 500 ,425) # right, left, middle
}

skeleton_bounds = {
    'left_shoulder': (120, 60), #up, down
    'left_elbow': (120, 60), #far, close
    'right_shoulder': (60, 120), #down, up
    'right_elbow': (60, 120), #close, far
    'torso': (156, 356), # right, left, middle
    'neck': (135, 195) # right, left, middle
}

joints_to_angles = {
    'right_elbow': ['right_shoulder', 'right_elbow', 'right_hand'],
    'left_elbow': ['left_shoulder', 'left_elbow', 'left_hand'],
    'right_shoulder': ['right_elbow', 'right_shoulder', 'right_hip'],
    'left_shoulder': ['left_elbow', 'left_shoulder', 'left_hip'],
    'neck': ['left_eye', 'right_eye', 'left_shoulder', 'right_shoulder'],
    # 'torso': ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder'],
}


def moving_average(data, window_size):
    padding = window_size // 2
    padded_data = np.pad(data, (padding, padding), mode='edge')
    filtered_data = np.convolve(padded_data, np.ones(window_size), 'same') / window_size
    return filtered_data
