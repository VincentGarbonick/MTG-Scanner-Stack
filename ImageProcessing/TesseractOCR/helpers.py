import difflib
import json
import requests
import urllib.request
import pytesseract
import PIL.ImageFilter
import mysql.connector
import sys
import hashlib
import threading
import time
import tempfile
from PIL import Image, ImageDraw, ImageColor, ImageEnhance, ImageOps
import os

SQL_USER = "root"
SQL_PASS = ""
SQL_DB_NAME = "magic"
SQL_SOCK_LAMPP = "/opt/lampp/var/mysql/mysql.sock"
SQL_SOCK = "/var/run/mysqld/mysqld.sock"


#crop = (left, top, right, bottom)
# These values will need to be adjusted to crop the title area depending on our camera
CROP_COORDS = (342, 291, 800, 350)
CROP_COORDS = (39, 39, 390, 69)
CROP_COORDS = (680, 700, 1560, 760)
ORIGINAL_CROP = (1505, 410, 1910, 485)
ROTATED_CROP = (1280, 560, 1760, 640)

def connectDatabase():
    """
    Connects to the MySQL database

    :return: mysql.connector.connection object
    """
    sqlConnection = mysql.connector.connect(
        user=SQL_USER,
        passwd=SQL_PASS,
        db=SQL_DB_NAME,
        unix_socket=SQL_SOCK)
    return sqlConnection

def incrementValue(keyName, valueName = "qty"):
    """
    Increments a value in the database by + 1
    :param keyName: The primary key to be updated, usually "cardName"
    :param valueName: The value to be incremented, by default "qty"
    :return: 0 - success
    """
    connection = connectDatabase()
    cur = connection.cursor()
    try:
        print(f"NEW ENTRY:\nINSERT INTO mtgCards VALUES ('{keyName}', 0, 0, 1)")
        print(f"EXISTING ENTRY:\nUPDATE mtgCards SET {valueName} = {valueName} + 1 WHERE cardName = '{keyName}'")
        escapedName = keyName.replace( "'", "''")
        cur.execute(f"INSERT INTO mtgCards VALUES ('{escapedName}', 0, 0, 1)")
        print(f"Added new entry ({keyName}, 1, 0)")
    except mysql.connector.errors.IntegrityError as e:
        try:
            cur.execute(f"UPDATE mtgCards SET {valueName} = {valueName} + 1 WHERE cardName = '{escapedName}'")
            print(f"Incremented entry {keyName}")
        except Exception as e:
            print(e)
            return 1
    connection.commit()
    connection.close()
    return 0


def imageCropVisual(PILImage, cropVals=ORIGINAL_CROP):
    """
    Creates a image file that has outlined the crop area and saves it to current directory for viewing/testing purposes

    :param PILImage: PIL Image object 
    :param cropVals: Crop values used to crop the image
    :return: 0 - success
    """

    
    
#crop = (left, top, right, bottom)
    draw = ImageDraw.Draw(PILImage)
    # Top line
    draw.line(
        [(cropVals[0], cropVals[1]), (cropVals[2], cropVals[1])],
        fill = 0,
        width = 4
    )
    # Bottom line
    draw.line(
        [(cropVals[0], cropVals[3]), (cropVals[2], cropVals[3])],
        fill = 0,
        width = 4
    )
    # Left line
    draw.line(
        [(cropVals[0], cropVals[1]), (cropVals[0], cropVals[3])],
        fill = 0,
        width = 4
    )
    # Right line
    draw.line(
        [(cropVals[2], cropVals[1]), (cropVals[2], cropVals[3])],
        fill = 0,
        width = 4
    )
    hash = hashlib.md5(bytes(PILImage.tobytes()))
    PILImage.save(f"Cropped_{hash.hexdigest()[0:7]}.jpeg")
    return 0


def processImage(imageFile, crop1, crop2, returnVals, index):
    """
    Creates a copy of image and rotates it. Both images are then cropped, filtered, and returned as a tuple.
    The first image in the tuple is the original image, the second is the rotated image.

    :param imageFile: File of image to be processed
    :return: Returns 2 images that have been processed and should be ready for character recognition
    """
    try:
        image = Image.open(imageFile)
        rotatedCopy = Image.open(imageFile)
    except Exception as e:
        print(f"Could not open image file {imageFile} - {e}")
        return 1

    # Create a copy that is rotated 180 degrees to work for both input cases
    image = image.rotate(90)
    rotatedCopy = rotatedCopy.rotate(90)
    rotatedCopy = rotatedCopy.rotate(180)
    imageCropVisual(image, cropVals = crop1)
    imageCropVisual(rotatedCopy, cropVals = crop2)

    border = (10, 10, 10, 10)
        
    imageUpright = image.crop(crop1)
    width, height = imageUpright.size
    newSize = (width * 2, height * 2)
    imageUpright = imageUpright.resize(newSize, PIL.Image.BILINEAR)
    imageUpright = PIL.ImageOps.expand(imageUpright, border=border, fill=0)
    enhancer = ImageEnhance.Contrast(imageUpright)
    imageUpright = enhancer.enhance(4)
    imageUpright = imageUpright.convert('L')
    imageUpright = imageUpright.filter(PIL.ImageFilter.UnsharpMask(10, 200, 2))

    imageUpright.save("UPRIGHT PROCESSED.jpg")

    rotatedImage = image.crop(crop2)
    width, height = rotatedImage.size
    newSize = (width * 2, height * 2)
    rotatedImage = rotatedImage.resize(newSize, PIL.Image.BILINEAR)
    rotatedImage = PIL.ImageOps.expand(rotatedImage, border=border, fill=0)
    enhancer = ImageEnhance.Contrast(rotatedImage)
    rotatedImage = enhancer.enhance(4)
    rotatedImage = rotatedImage.convert('L')
    rotatedImage = rotatedImage.filter(PIL.ImageFilter.UnsharpMask(10, 200, 2))

    rotatedImage.save("ROTATED PROCESSED.jpg")

    returnVals[index] = (imageUpright, rotatedCopy)
    return 0

def textFromImage(image, index, returnVals):
    """
    Uses tesseract to convert an image to string

    :param image: Image file to convert to string
    :return: text recovered from the image
    """
    text = pytesseract.image_to_string(image)
    text = text.split('\n')[0]
    print(f"Text from image: [{text}]")
    returnVals[index] = text


class nameMatch:
    def __init__(self, matchList, ratio):
        self.matchList = matchList
        if len(matchList) > 0:
            self.matchName = matchList[0]
        else:
            self.matchName = ""
        self.ratio = ratio


def getCloseMatches(cardName, namesList, index, returnVals, cutoff=0.6, num=1):
    """
    Gets the closest match(s) to cardName from the list of all names in cardNames.json

    :param cardName: The card name string to find a match of
    :param namesList: A list containing all possible names
    :param cutoff: 0-1 float that defines the lowest "closeness" ratio acceptable
    :param num: Number of matches to return
    :return: Returns a tuple containing a (len(possibilities) list of matches, and ratio float of match closeness)
             If ratio is 0, no matches were found.
    """
    try:
        with open("cardNames.json", mode="r") as file: 
            namesList = json.loads(file.read())
    except Exception as e:
        print(f"Could not read cardNames.json - {e}")
        return 1
    similarList = difflib.get_close_matches(cardName, n=num, possibilities=namesList, cutoff=cutoff)
    ratio = 0
    if num == 1 and len(similarList) > 0:
        ratio = difflib.SequenceMatcher(None, similarList[0], cardName).ratio()
    returnVals[index] = nameMatch(similarList, ratio)


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
