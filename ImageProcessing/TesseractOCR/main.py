
from helpers import *


import ARDUINO

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
    #print(getCloseMatches("Word Brer"))
    #images = processImage(r"ImageTemp/Fury Sliver Rotated.jpeg")
    #text = textFromImage(images[1])
    #print(text)
    #print(getCloseMatches(text))

    #initialize()
    print("Starting camera module...")
    threadStop = False
    cameraThread = threading.Thread(target=ARDUINO.main, args = (lambda : threadStop, ))
    #cameraThread.start()
    print("Camera thread started")

    namesList = []
    try:
        with open("cardNames.json", mode="r") as file: 
            namesList = json.loads(file.read())
    except Exception as e:
        print(f"Could not read cardNames.json - {e}")
        sys.exit(1)

    print("Starting image processing")

    try:
        while True:
            # Check if there are any files in ImageTemp/ directory
            if len(os.listdir("ImageTemp")) > 0:
                *_, (paths, names, files) = os.walk("ImageTemp")
                modifiedTimes = {}
                for i in files:
                    modifiedTimes[i] = os.path.getmtime(fr"ImageTemp/{i}")
                # Get the file with the oldest last modified time
                oldestFile = max(modifiedTimes, key=modifiedTimes.get)

                #crop = (left, top, right, bottom)
                crops1 = [(1100, 805, 1900, 840), (1100, 820, 1900, 855), (1100, 835, 1900, 870)]
                crops2 = [(1170, 800, 2000, 845), (1170, 815, 2000, 860), (1170, 830, 2000, 875)]


                parallelProcessThreads = []
                imageResults = [0] * len(crops1)
                for i, (c1, c2) in enumerate(zip(crops1, crops2)):
                    newThread = threading.Thread(target=processImage, args=(fr"ImageTemp/{oldestFile}", c1, c2, imageResults, i))
                    parallelProcessThreads.append(newThread)
                
                print("Running image process threads.")
                for i in parallelProcessThreads:
                    i.start()
                for i in parallelProcessThreads:
                    i.join()
                parallelProcessThreads.clear()

                #sys.exit(0)

                originalImages = []
                rotatedImages = []
                for i in imageResults:
                    originalImages.append(i[0])
                    rotatedImages.append(i[1])
                
                originalTexts = [0] * len(crops1)
                rotatedTexts = [0] * len(crops2)

                for i, (original, rotated) in enumerate(zip(originalImages, rotatedImages)):
                    newThreadOriginal = threading.Thread(target=textFromImage, args=(original, i, originalTexts))
                    newThreadRotated = threading.Thread(target=textFromImage, args=(rotated, i, rotatedTexts))
                    parallelProcessThreads.append(newThreadOriginal)
                    parallelProcessThreads.append(newThreadRotated)

                print("Starting text from image threads.")
                for i in parallelProcessThreads:
                    i.start()
                for i in parallelProcessThreads:
                    i.join()
                parallelProcessThreads.clear()
                
                originalMatches = [0] * len(crops1)
                rotatedMatches = [0] * len(crops2)
                for i, (original, rotated) in enumerate(zip(originalImages, rotatedImages)):
                    newThreadOriginal = threading.Thread(target=getCloseMatches, args=(originalTexts[i], namesList, i, originalMatches))
                    newThreadRotated = threading.Thread(target=getCloseMatches, args=(rotatedTexts[i], namesList, i, rotatedMatches))
                    parallelProcessThreads.append(newThreadOriginal)
                    parallelProcessThreads.append(newThreadRotated)
                
                print("Starting match threads.")
                for i in parallelProcessThreads:
                    i.start()
                for i in parallelProcessThreads:
                    i.join()

                
                bestOriginalMatch = nameMatch([], 0)
                bestRotatedMatch = nameMatch([], 0)

                for _originalMatches, _rotatedMatches in zip(originalMatches, rotatedMatches):
                    if _originalMatches.ratio > bestOriginalMatch.ratio:
                        bestOriginalMatch = _originalMatches
                    if _rotatedMatches.ratio > bestRotatedMatch.ratio:
                        bestRotatedMatch = _rotatedMatches
                
                print(bestOriginalMatch.matchList, bestOriginalMatch.ratio)
                print(bestRotatedMatch.matchList, bestRotatedMatch.ratio)
                
                
                """
                if images == 1:
                    continue
                originalImage = images[0]
                rotatedImage = images[1]

                # Perform text recognition on images
                originalImageText = textFromImage(images[0])
                rotatedImageText = textFromImage(images[1])
                # Find a card name that most closely matches text from images
                originalImageMatch = getCloseMatches(originalImageText, namesList)
                rotatedImageMatch = getCloseMatches(rotatedImageText, namesList)

                # If no close card name matches are found from the images, remove the image and continue with next file
                if originalImageMatch.ratio == 0 and rotatedImageMatch.ratio == 0:
                    print(f"No matches found for {images} - [{originalImageText}, {rotatedImageText}]")
                    #os.remove(fr"ImageTemp/{oldestFile}")
                    continue

                # Determine which name has the closest match
                if originalImageMatch.ratio > rotatedImageMatch.ratio:
                    text = originalImageMatch.matchName
                else:
                    text = rotatedImageMatch.matchName

                # 'text' variable now contains the closest matching card name from the picture.
                print(f"Got card name match {text}")
                incrementValue(text)
                print(fr"Removing {oldestFile}")
                #os.remove(fr"ImageTemp/{oldestFile}")
                """

                if bestOriginalMatch.ratio == 0 and bestRotatedMatch.ratio == 0:
                    print(f"No matches found for ImageTemp/{oldestFile} - [{bestOriginalMatch.matchList}, {bestRotatedMatch.matchList}]")
                    os.remove(fr"ImageTemp/{oldestFile}")
                    continue
                    
                if bestOriginalMatch.ratio > bestRotatedMatch.ratio:
                    finalText = bestOriginalMatch.matchName
                else:
                    finalText = bestRotatedMatch.matchName
                print(f"Got card name match {finalText}")
                incrementValue(finalText)
                print(fr"Removing ImageTemp/{oldestFile}")
                os.remove(fr"ImageTemp/{oldestFile}")
            else:
                time.sleep(0.1)


    except KeyboardInterrupt:
        print("Stopping camera thread...")
        threadStop = True
        cameraThread.join(timeout=5)

