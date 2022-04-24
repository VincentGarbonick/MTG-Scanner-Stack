
from helpers import *
import ScanCards

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
    # initialize()

    """
    This would be running ScanCards.py in a separate thread, but the Jetson Nano seems to have trouble
    running both at the same time.
    """
    # print("Starting camera module...")
    # threadStop = False
    # cameraThread = threading.Thread(target=ScanCards.main, args = (lambda : threadStop, ))
    # cameraThread.start()
    # print("Camera thread started")

    namesList = []
    try:
        with open("cardNames.json", mode="r") as file: 
            namesList = json.loads(file.read())
    except Exception as e:
        print(f"Could not read cardNames.json - {e}")
        sys.exit(1)

    print("Starting Image Processing")

    # Check how many unrecognized images already exist as to not overwrite any existing images
    unrecognizedImageTotal = len(os.listdir("UnrecognizedImages"))

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
                # crops1 and crops 2 are a list of crop values for upright and rotated cards
                crops1 = [(1100, 805, 1900, 840), (1100, 820, 1900, 855), (1100, 835, 1900, 870)]
                crops2 = [(1170, 800, 2000, 845), (1170, 815, 2000, 860), (1170, 830, 2000, 875)]

                # Spawn threads to process image for each crop area
                parallelProcessThreads = []
                imageResults = [0] * len(crops1)
                for i, (c1, c2) in enumerate(zip(crops1, crops2)):
                    newThread = threading.Thread(target=processImage, args=(fr"ImageTemp/{oldestFile}", c1, c2, imageResults, i))
                    parallelProcessThreads.append(newThread)
                
                print("\nRunning Parallel Image Processing Threads")
                for i in parallelProcessThreads:
                    i.start()
                for i in parallelProcessThreads:
                    i.join()
                parallelProcessThreads.clear()
                print("Done")

                originalImages = []
                rotatedImages = []
                for i in imageResults:
                    originalImages.append(i[0])
                    rotatedImages.append(i[1])
                
                # Spawn threads to get any recognized text from all process images
                originalTexts = [0] * len(crops1)
                rotatedTexts = [0] * len(crops2)
                for i, (original, rotated) in enumerate(zip(originalImages, rotatedImages)):
                    newThreadOriginal = threading.Thread(target=textFromImage, args=(original, i, originalTexts))
                    newThreadRotated = threading.Thread(target=textFromImage, args=(rotated, i, rotatedTexts))
                    parallelProcessThreads.append(newThreadOriginal)
                    parallelProcessThreads.append(newThreadRotated)

                print("\nStarting Parallel Text Recognition Threads")
                for i in parallelProcessThreads:
                    i.start()
                for i in parallelProcessThreads:
                    i.join()
                parallelProcessThreads.clear()
                print("Done")
                

                # Spawn threads to find card name matches for all recognized text
                originalMatches = [0] * len(crops1)
                rotatedMatches = [0] * len(crops2)
                for i, (original, rotated) in enumerate(zip(originalImages, rotatedImages)):
                    newThreadOriginal = threading.Thread(target=getCloseMatches, args=(originalTexts[i], namesList, i, originalMatches))
                    newThreadRotated = threading.Thread(target=getCloseMatches, args=(rotatedTexts[i], namesList, i, rotatedMatches))
                    parallelProcessThreads.append(newThreadOriginal)
                    parallelProcessThreads.append(newThreadRotated)
                
                print("\nStarting Parallel Text Matching Threads")
                for i in parallelProcessThreads:
                    i.start()
                for i in parallelProcessThreads:
                    i.join()

                # Find the match with the highest ratio for both the original and rotated images
                bestOriginalMatch = nameMatch([], 0)
                bestRotatedMatch = nameMatch([], 0)

                for _originalMatches, _rotatedMatches in zip(originalMatches, rotatedMatches):
                    if _originalMatches.ratio > bestOriginalMatch.ratio:
                        bestOriginalMatch = _originalMatches
                    if _rotatedMatches.ratio > bestRotatedMatch.ratio:
                        bestRotatedMatch = _rotatedMatches
                print("Done\n")
                
                print(bestOriginalMatch.matchList, bestOriginalMatch.ratio)
                print(bestRotatedMatch.matchList, bestRotatedMatch.ratio)

                if bestOriginalMatch.ratio == 0 and bestRotatedMatch.ratio == 0:
                    
                    # Save unrecognized image in the UnrecognizedImages directory with the next lowest index
                    unrecognizedImageTotal += 1
                    print(f"/nNo matches found for ImageTemp/{oldestFile} - [{bestOriginalMatch.matchList}, {bestRotatedMatch.matchList}]")
                    print(f"Saving Image as UnrecognizedImages/Unrecognized_Image_{unrecognizedImageTotal}")
                    tempImage = Image.open(fr"ImageTemp/{oldestFile}")
                    tempImage.save(f"UnrecognizedImages/Unrecognized_Image_{unrecognizedImageTotal}.jpg")
                    os.remove(fr"ImageTemp/{oldestFile}")
                    continue
                
                # Decide whether the rotated or original image has the better match
                if bestOriginalMatch.ratio > bestRotatedMatch.ratio:
                    finalText = bestOriginalMatch.matchName
                else:
                    finalText = bestRotatedMatch.matchName

                print(f"\nGot card name match {finalText}")
                # Increment the database entry for the final match
                incrementValue(finalText)

                # Remove processed image file
                print(fr"Removing ImageTemp/{oldestFile}")
                os.remove(fr"ImageTemp/{oldestFile}")

            else:
                time.sleep(0.1)


    except KeyboardInterrupt:
        
        print("\nStopping program")

        # print("Stopping camera thread...")
        # threadStop = True
        # cameraThread.join(timeout=5)

