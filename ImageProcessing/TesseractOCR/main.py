import pytesseract
from PIL import Image
from helpers import *

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
    print(getCloseMatches("Fur Sliver"))
