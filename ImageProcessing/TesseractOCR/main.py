
from helpers import *
import os, time
"""
This will be the main file for handling image processing on the Jetson Nano.
Images will be acquired from a separate program that will be in control of motor and camera.
This program will save captured pictures to the 'ImageTemp' directory.
Images in this directory will then be processed as a FIFO queue. 
Processed images will be added to the database. 

"""

def initialize():
    """
    Initializes all necessary data. This includes updating the default cards JSON file from the Scryfall API
    and populating a JSON of all card names from the default cards object.

    :return: None
    """
    updateDefaultCardsJSON()
    generateCardNames()



if __name__ == "__main__":
    initialize()
    #print(getCloseMatches("Word Brer"))
    #images = processImage(r"ImageTemp/Fury Sliver Rotated.jpeg")
    #text = textFromImage(images[1])
    #print(text)
    #print(getCloseMatches(text))

    """
    while True:
        get all files in ImageTemp/
        Sort by oldest file modified
        Process that file to get a card name from 
    """
    while True:
        if len(os.listdir("ImageTemp")) > 0:
            for (paths, names, files) in os.walk("ImageTemp"):
                modifiedTimes = {}
                for i in files:
                    modifiedTimes[i] = os.path.getmtime(fr"ImageTemp/{i}")
                oldestFile = max(modifiedTimes, key=modifiedTimes.get)
                break
            images = processImage(fr"ImageTemp/{oldestFile}")
            texts = (textFromImage(images[0]), textFromImage(images[1]))
            texts = (getCloseMatches(texts[0]), getCloseMatches(texts[1]))
            if texts[0][1] == 0 and texts[1][1] == 0:
                print(f"No matches found for {images} - {texts}")
                os.remove(fr"ImageTemp/{oldestFile}")
                continue
            if texts[0][1] > texts[1][1]:
                text = texts[0][0][0]
            else:
                text = texts[1][0][0]

            print(f"Got card name match {text}")
            print(fr"Removing {oldestFile}")
            os.remove(fr"ImageTemp/{oldestFile}")
            time.sleep(0.1)
