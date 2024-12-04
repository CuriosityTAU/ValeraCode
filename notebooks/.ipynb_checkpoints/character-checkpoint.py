import pygame
import os
import sys
import time
from PIL import Image
import math
from gtts import gTTS
import platform
import threading

print("Setting character ...")

# Initialize pygame
pygame.init()

# Set up the full-screen display
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
# screen = pygame.display.set_mode((infoObject.current_w/2, infoObject.current_h/2))

# Path to the directory containing the images
image_folder_path = 'assets/face/'

global_parts = ["Eyes", "Nose", "Mouth"]
the_character = "valera"

characters = {
    'valera': {
        "name": "valera",
        "base_image_name": "robot face.00",
        "part_slices": {"Eyes": [0, 0.41], "Nose": [0.41, 0.65], "Mouth": [0.65, 1]},
        "part_sequence": {
            "Eyes": [("idle", [1]), ("blink", [i for i in range(1,8)])], 
            "Mouth": [("idle", [1]), ("talk", [i for i in range(1,5)])], 
            "Nose": [("idle", [1])]}
    },
    'fuzzy': {
        "name": "fuzzy",
        "base_image_name": "fuzzy face.00",
        "part_slices": {"Eyes": [0, 0.41], "Nose": [0.41, 0.65], "Mouth": [0.65, 1]},
        "part_sequence": {
            "Eyes": [("idle", [1]), ("blink", [i for i in range(1,8)])], 
            "Mouth": [("idle", [1]), ("talk", [i for i in range(1,5)])], 
            "Nose": [("idle", [1])]}
    },
    'tutti': {
        "name": "tutti",
        "base_image_name": "tutti face.00",
        "part_slices": {"Eyes": [0, 0.41], "Nose": [0.41, 0.65], "Mouth": [0.65, 1]},
        "part_sequence": {
            "Eyes": [("idle", [1]), ("blink", [i for i in range(1,8)])], 
            "Mouth": [("idle", [1]), ("talk", [i for i in range(1,5)])], 
            "Nose": [("idle", [1])]}
    }
}

def initialize_character(character_=the_character, save=False):
    character_folder_path = image_folder_path + character_["name"] + "/"
    if save:
        if not os.path.exists(character_folder_path):
            os.mkdir(character_folder_path)
                              
        # global initialization
        for part in global_parts:
            if not os.path.exists(character_folder_path + part):
                os.mkdir(character_folder_path + part)
    
    # character variables
    image_name = image_folder_path + character_["base_image_name"]
    character_["images"] = {}
    
    # go over all the data in the sequence
    for part, part_sequence in character_["part_sequence"].items():
        part_slice = character_["part_slices"][part]
        character_["images"][part] = {}
        for part_data in part_sequence:
            character_["images"][part][part_data[0]] = {}
            for i in part_data[1]:
                file_name = character_folder_path + part + "/" + part_data[0]
                file_name = f"{file_name}_slice_{i}.png"

                if save:
                    # Open the image
                    image = Image.open(f"{image_name}{i}.png")
                    # Get the dimensions of the image
                    width, height = image.size
                    sliced_image = image.crop((0, math.floor(height * part_slice[0]), width, math.floor(height * part_slice[1])))
                    sliced_image.save(f"{file_name}")
                else:
                    sliced_image = Image.open(f"{file_name}")
                character_["images"][part][part_data[0]][str(i)] = sliced_image
    return character_

def set_character_face(parts_selected, character_name="valera"):
    character = characters[character_name]
    # default
    images = {}
    for part in global_parts:
        images[part] = None
    for part, sequence in parts_selected.items():
        images[part] = character["images"][part][sequence[0]][sequence[1]]
    for part in global_parts:
        if not images[part]:
            images[part] = character["images"][part]["idle"]["1"]
            
    # Get the maximum width among all images
    max_width = max(img.width for img in images.values())

    # Resize images to have the same width (optional)
    for part in global_parts:
        images[part] = images[part].resize((max_width, images[part].height))

    # Calculate the total height of the stacked images
    total_height = sum(img.height for img in images.values())

    # Create a new blank image with the maximum width and total height
    stacked_image = Image.new('RGB', (max_width, total_height), color='white')

    # Paste each image onto the new image
    y_offset = 0
    for part in global_parts:
        stacked_image.paste(images[part], (0, y_offset))
        y_offset += images[part].height

    # convert to pygame_image
    pygame_image = pygame.image.fromstring(stacked_image.tobytes(), stacked_image.size, stacked_image.mode)
    return pygame_image


def character_face_thread(parts_selected, stop_event=None, stop_condition=None, delay=0.2, character_name="valera"):
    max_length = 0
    for part, part_data in parts_selected.items():
        max_length = max(max_length, len(part_data[1]))

    for i in range(max_length):
        face = {}
        for part, part_data in parts_selected.items():
            if i < len(part_data[1]):
                face[part] = (part_data[0], part_data[1][i])
        face_image = set_character_face(face, character_name)
        display_character_face(face_image)
        time.sleep(delay)
    
        if stop_event:
            if stop_event.is_set():
                break

    # if the stop condition is the speech, send the stop event
    if "face" in stop_condition:
        stop_event.set()


def display_character_face(image_):
    # Scale the image to fill the screen
    image_ = pygame.transform.scale(image_, (infoObject.current_w, infoObject.current_h))

    # Blit the image to the screen
    screen.blit(image_, (0, 0))

    # Update the display
    pygame.display.flip()

# initialize_character(characters['tutti'], save=True)

# Clean up and quit
# pygame.quit()