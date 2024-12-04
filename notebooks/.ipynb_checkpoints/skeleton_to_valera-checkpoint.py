from global_definitions import *
import json
from copy import deepcopy
import matplotlib.pyplot as plt


def calculate_angle(pointA, pointB, pointC):
    # Create vectors
    vectorA = np.array(pointA) - np.array(pointB)
    vectorB = np.array(pointC) - np.array(pointB)

    # Calculate dot product
    dot_product = np.dot(vectorA, vectorB)

    # Calculate the magnitudes of the vectors
    magnitudeA = np.linalg.norm(vectorA)
    magnitudeB = np.linalg.norm(vectorB)

    # Calculate the cosine of the angle
    cos_angle = dot_product / (magnitudeA * magnitudeB)

    # Calculate the angle in radians, and then convert to degrees
    angle = np.arccos(cos_angle)
    angle_degrees = np.degrees(angle)

    return angle_degrees


def calculate_angle_between_lines(pointA, pointB, pointC, pointD):
    # Create vectors
    vector1 = np.array(pointB) - np.array(pointA)
    vector2 = np.array(pointD) - np.array(pointC)

    # Calculate dot product
    dot_product = np.dot(vector1, vector2)

    # Calculate the magnitudes of the vectors
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)

    # Calculate the cosine of the angle
    if magnitude1 != 0 and magnitude2 != 0:
        cos_angle = dot_product / (magnitude1 * magnitude2)
    else:
        cos_angle = 0.0

    # Calculate the angle in radians, and then convert to degrees
    angle = np.arccos(cos_angle)
    angle_degrees = 90.0 - np.degrees(angle)

    if np.isnan(angle_degrees):
        angle_degrees = 180.0

    return angle_degrees

def convert_to_valera_angles(angle):
    valera_angle_ = {}
    for k, v in angle.items():
        norm_angle = None
        for which_angle in joints_to_angles:
            if which_angle in k:
                s_bounds = skeleton_bounds[which_angle]
                norm_angle = ((v - s_bounds[0]) / (s_bounds[1] - s_bounds[0]))
            if norm_angle:
                valera_angle_[k] = int((1 - norm_angle) * motor_bounds[k][0] + norm_angle * motor_bounds[k][1])
    return valera_angle_


def convert_skeletons_to_sequence(skeletons):
    data = {
        'skeleton': [],
        'valera': [],
        'time': []
    }
    sequence_ = []

    t = 0
    skeleton_angles = {}
    for ang, joint in joints_to_angles.items():
        if ang not in skeleton_angles:
            skeleton_angles[ang] = []
        for skeleton in skeletons:
            if len(joint) == 3:
                skeleton_angles[ang].append(calculate_angle(skeleton[joint[0]], skeleton[joint[1]], skeleton[joint[2]]))
            elif len(joint) == 4:
                skeleton_angles[ang].append(calculate_angle_between_lines(skeleton[joint[0]], skeleton[joint[1]],
                                                                          skeleton[joint[2]], skeleton[joint[3]]))
            
        skeleton_angles[ang] = moving_average(skeleton_angles[ang], 10)
        
    for i in range(len(skeletons)):
        skeleton_ang = {}
        for k, v in skeleton_angles.items():
            skeleton_ang[k] = v[i]

        valera_angles = convert_to_valera_angles(skeleton_ang)
        movement = {
            'time': deepcopy(t),
            'motors': deepcopy(valera_angles)
        }
        sequence_.append(movement)
        t += skeleton['duration']

        data['skeleton'].append(skeleton_ang['right_elbow'])
        data['valera'].append(valera_angles['right_elbow'])
    #plt.plot(data['skeleton'])
    #plt.show()
    #plt.plot(data['valera'])
    #plt.show()

    return sequence_
    
# skeletons = json.load(open('assets/movement/lesson_01/aalag_alag.json', 'r'))
# sequence = convert_skeletons_to_sequence(skeletons)
# print(sequence)