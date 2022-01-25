
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
    if not os.path.isdir("ImageTemp"):
        os.mkdir("ImageTemp")
    updateDefaultCardsJSON()
    generateCardNames()
    print("Initialization complete")



if __name__ == "__main__":
    initialize()
    #print(getCloseMatches("Word Brer"))
    #images = processImage(r"ImageTemp/Fury Sliver Rotated.jpeg")
    #text = textFromImage(images[1])
    #print(text)
    #print(getCloseMatches(text))

    while True:
        # Check if there are any files in ImageTemp/ directory
        if len(os.listdir("ImageTemp")) > 0:
            *_, (paths, names, files) = os.walk("ImageTemp")
            modifiedTimes = {}
            for i in files:
                modifiedTimes[i] = os.path.getmtime(fr"ImageTemp/{i}")
            # Get the file with the oldest last modified time
            oldestFile = max(modifiedTimes, key=modifiedTimes.get)

            # Get cropped and filtered images from the oldest file
            images = processImage(fr"ImageTemp/{oldestFile}")
            # Perform text recognition on images
            texts = (textFromImage(images[0]), textFromImage(images[1]))
            # Find a card name that most closely matches text from images
            texts = (getCloseMatches(texts[0]), getCloseMatches(texts[1]))

            # If no close card name matches are found from the images, remove the image and continue with next file
            if texts[0][1] == 0 and texts[1][1] == 0:
                print(f"No matches found for {images} - {texts}")
                os.remove(fr"ImageTemp/{oldestFile}")
                continue

            # Determine which name has the closest match
            if texts[0][1] > texts[1][1]:
                text = texts[0][0][0]
            else:
                text = texts[1][0][0]

            # 'text' variable now contains the closest matching card name from the picture.
            print(f"Got card name match {text}")
            print(fr"Removing {oldestFile}")
            os.remove(fr"ImageTemp/{oldestFile}")