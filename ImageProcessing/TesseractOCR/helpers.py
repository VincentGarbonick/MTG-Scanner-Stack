import difflib
import json
from cv2 import IMREAD_GRAYSCALE
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
import cv2
import numpy
from PIL import Image, ImageDraw, ImageColor, ImageEnhance, ImageOps
import os

SQL_USER = "root"
SQL_PASS = ""
SQL_DB_NAME = "magic"
SQL_SOCK_LAMPP = "/opt/lampp/var/mysql/mysql.sock"
SQL_SOCK = "/var/run/mysqld/mysqld.sock"


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
        cur.execute(f"INSERT INTO mtgCards VALUES ('{escapedName}', 1, 0, 0)")
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
    :param crop1: Crop areas for upright card images
    :param crop2: Crop areas for flipped card images
    :param returnVals: List of return values for each thread when joined.
    :param index: Thread index used for returnVals
    :return: A tuple of two card images are stored in returnVals at the current thread index.
        returns 0 on success. 
    """
    try:
        image = Image.open(imageFile)
    except Exception as e:
        print(f"Could not open image file {imageFile} - {e}")
        return 1

    # Create a copy that is rotated 180 degrees to work for both input cases
    rotatedCopy = image.copy()
    rotatedCopy = rotatedCopy.rotate(180)
    
    # Crop the image to the given area of interest
    imageUpright = image.crop(crop1)

    # Increase the image contrast by 180%
    enhancer = ImageEnhance.Contrast(imageUpright)
    imageUpright = enhancer.enhance(1.8)

    # Convert image to 8bit black and white
    imageUpright = imageUpright.convert('L')

    # Apply a median filter
    imageUpright = imageUpright.filter(PIL.ImageFilter.MedianFilter())

    imageUpright.save(f"UPRIGHT PROCESSED{index}.jpg")

    # Repeat process for rotated image
    rotatedImage = rotatedCopy.crop(crop2)
    enhancer = ImageEnhance.Contrast(rotatedImage)
    rotatedImage = enhancer.enhance(1.8)
    rotatedImage = rotatedImage.convert("L")
    rotatedImage = rotatedImage.filter(PIL.ImageFilter.MedianFilter())

    rotatedImage.save(f"ROTATED PROCESSED{index}.jpg")

    returnVals[index] = (imageUpright, rotatedImage)
    return 0


def textFromImage(image, index, returnVals):
    """
    Uses tesseract to convert an image to string

    :param image: Image file to convert to string
    :param index: Thread index used for returnVals
    :param returnVals: List of return values for each thread when joined.
    :return: Text recovered from image is stored in returnVals at the current thread index.
    """
    text = pytesseract.image_to_string(image)
    text = text.split('\n')
    text = [i for i in text if len(i) >= 3]
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
    :param index: Thread index used for returnVals
    :param returnVals: List of return values for each thread when joined.
    :param cutoff: 0-1 float that defines the lowest "closeness" ratio acceptable
    :param num: Number of matches to return
    :return: A nameMatch object is stored in returnVals at the current thread index.
    """
    try:
        with open("cardNames.json", mode="r") as file: 
            namesList = json.loads(file.read())
    except Exception as e:
        print(f"Could not read cardNames.json - {e}")
        return 1
    similarLists = []
    for i in cardName:
        if len(i) > 3:
            similarList = difflib.get_close_matches(i, n=num, possibilities=namesList, cutoff=cutoff)
            ratio = 0
            if len(similarList) > 0:
                ratio = difflib.SequenceMatcher(None, similarList[0], i).ratio()
            similarLists.append((similarList, ratio))

    highest = [([""], 0)]
    for i in similarLists:
        if i[1] > highest[0][1]:
            highest[0] = i

    returnVals[index] = nameMatch(highest[0][0], highest[0][1])


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
