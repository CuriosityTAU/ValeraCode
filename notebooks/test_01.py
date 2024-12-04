from behaviors import *
from skeleton_to_valera import *
from movement import *

skeletons = json.load(open('assets/movement/aalag_alag.json', 'r'))
sequence = convert_skeletons_to_sequence(skeletons)
# move_sequence(sequence)

behavior = [
    {
        "movement": sequence,
        "audio": "assets/audio/aalag_alag.wav",
        "type": ["sound"],
        "stop": ["movement"]
    }
]

run_behavior(behavior)