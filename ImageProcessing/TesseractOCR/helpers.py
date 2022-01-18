import json, requests, urllib.request, difflib

import PIL.ImageFilter
import pytesseract
from PIL import Image


def processImage(imageFile):
    """
    Creates a copy of image and rotates it. Both images are then cropped, filtered, and returned as a tuple.
    The first image in the tuple is the original image, the second is the rotated image.

    :param imageFile: File of image to be processed
    :return: Returns 2 images that have been processed and should be ready for character recognition
    """
    try:
        image = Image.open(imageFile)
    except Exception as e:
        print(f"Could not open image file {imageFile} - {e}")
        return 1

    #crop = (left, top, right, bottom)
    # These values will need to be adjusted to crop the title area depending on our camera
    originalCrop = (39, 39, 390, 69)
    rotatedCrop = (95, 611, 447, 642)

    rotatedCopy = image.rotate(180)
    image = image.crop(originalCrop)
    image = image.convert('L')
    image = image.filter(PIL.ImageFilter.MedianFilter())
    rotatedCopy = rotatedCopy.crop(rotatedCrop)
    rotatedCopy = rotatedCopy.convert('L')
    rotatedCopy = rotatedCopy.filter(PIL.ImageFilter.MedianFilter())

    return image, rotatedCopy

def textFromImage(image):
    """
    Uses tesseract to convert an image to string

    :param image: Image file to convert to string
    :return: text recovered from the image
    """
    text = pytesseract.image_to_string(image)
    text = text.split('\n')[0]
    return text





def getCloseMatches(cardName, cutoff=0.6, num=1):
    """
    Gets the closest match(s) to cardName from the list of all names in cardNames.json

    :param cardName: The card name string to find a match of
    :param cutoff: 0-1 float that defines the lowest "closeness" ratio acceptable
    :param num: Number of matches to return
    :return: Returns a tuple containing a (len(possibilities) list of matches, and ratio float of match closeness)
    """
    try:
        with open("cardNames.json", mode="r") as file:
            namesList = json.loads(file.read())
    except Exception as e:
        print(f"Could not read cardNames.json - {e}")
        return 1
    similarList = difflib.get_close_matches(cardName, n=num, possibilities=namesList, cutoff=cutoff)
    ratio = None
    if num == 1 and len(similarList) > 0:
        ratio = difflib.SequenceMatcher(None, similarList[0], cardName).ratio()
    return (similarList, ratio)


def generateCardNames(cardsJson = "defaultCards.json", output = "cardNames.json"):
    """
    Reads in all card names from the supplied cardsJson file.
    Names are then written to the output file as a json file for referencing.

    :param cardsJson: Scryfall cards JSON file
    :param output: Output file name
    :return: 0 - success
    """
    names = []
    print(f"Reading cards file {cardsJson}")
    try:
        with open(cardsJson, mode="r") as file:
            cardsJson = json.loads(file.read())
    except Exception as e:
        print(f"Could not read file {cardsJson} - {e}")
        return 1

    for entries in cardsJson:
        try:
            names.append(entries["name"])
        except KeyError:
            print(f"No name entry for {entries}")
            return 1


    try:
        with open(output, mode="w") as file:
            print(f"Writing {len(names)} names to file {output}")
            file.write(json.dumps(names))
            print("Done")
            return 0
    except Exception as e:
        print(f"Could not write file {output} - {e}")
        return 1

def updateDefaultCardsJSON(output = "defaultCards.json", overwrite = False):
    """
    Updates the Scryfall Default Cards JSON file to the newest from the API.

    :param output: Output file name
    :param overwrite: Override to overwrite the defaultCards JSON even if updated_at matches
    :return: 0 - success
    """
    if overwrite == False:
        currentLastUpdate = None
        try:
            with open("bulkData.json") as currentFile:
                currentJSON = json.loads(currentFile.read())
            try:
                currentLastUpdate = currentJSON["updated_at"]
            except KeyError:
                print("Could not get updated_at of current file; Overwriting old file.")
                overwrite = True
        except Exception as e:
            print(f"Could not read current bulkData.json file.  {e}")
            overwrite = True


    requestData = requests.get("https://api.scryfall.com/bulk-data/default-cards")
    if requestData.status_code == 200:
        requestText = requestData.text
        requestJSON = json.loads(requestText)
        print(f"Got response\n{json.dumps(requestJSON, indent=4)}")

        try:
            with open("bulkData.json", mode="w") as bulkDataFile:
                bulkDataFile.write(json.dumps(requestJSON, indent=4))
        except Exception as e:
            print(f"Could not open bulkData.json for writing - {e}")

        if overwrite == False:
            try:
                lastUpdated = requestJSON["updated_at"]
                if currentLastUpdate == lastUpdated:
                    print("Current file is up to date. New file will not be downloaded.")
                    return 0
            except KeyError:
                print("Could not get last updated time, new file will be downloaded.")

        try:
            requestURI = requestJSON["download_uri"]
        except KeyError:
            print(f"Could not get download_uri from {requestJSON}")
            return 1

        print(f"Downloading JSON {requestURI}")
        with urllib.request.urlopen(requestURI) as downloadFile:
            downloadJSON = json.loads(downloadFile.read())
            print(f"Writing {output} file")
            try:
                with open(output, mode="w") as outputFile:
                    outputFile.write(json.dumps(downloadJSON, indent=4))
                    print("Done")
                    return 0
            except Exception as e:
                print(f"Could not write {output} file - {e}")
                return 1
    else:
        print(f"Bad request ({requestData.status_code}) - {requestData.reason}")
        return 1


if __name__ == "__main__":
    updateDefaultCardsJSON()
    generateCardNames()
