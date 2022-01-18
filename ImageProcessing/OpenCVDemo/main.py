import PIL.ImageFilter
import requests, json, urllib.request, os, time
from PIL import Image, ImageOps
import difflib

import pytesseract

# This directory was originally named OpenCVDemo since we thought we would be using OpenCV
# However, since we really only need character recognition, Google's open source Tesseract OCR was used for the demo.
pytesseract.pytesseract.tesseract_cmd = "tesseract.back"

# Used to get the JSON file of all Scryfall English card objects
# Note: This JSON file is very large and can take some time to download.
def getDefaultCardsJson():
    r = requests.get("https://api.scryfall.com/bulk-data/default-cards")
    if r.status_code == 200:
        requestData = r.text
        requestJSON = json.loads(requestData)
        print(f"Got response\n{json.dumps(requestJSON, indent=4)}")
        downloadURI = requestJSON["download_uri"]

        print("Downloading JSON")
        with urllib.request.urlopen(downloadURI) as download:
            downloadContent = json.loads(download.read())
            print("Writing file")
            with open("defaultCards.json", mode="w") as file:
                file.write(json.dumps(downloadContent, indent=4))
    else:
        print(f"Error in request: {r.status_code} - {r.reason}")


def getCardDetails(name):
    r = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={name.replace(' ', '+')}")
    time.sleep(0.05)
    if r.status_code == 200:
        requestData = r.text
        requestJSON = json.loads(requestData)
        if requestJSON["name"] != name:
            print(f"WARNING: API card name {requestJSON['name']} does not match {name}.")
            matchRatio = difflib.SequenceMatcher(None, name, requestJSON["name"]).ratio()
            if matchRatio > 0.25:
                print(f"ERROR: Resulting name ratio difference is too high: {matchRatio}")
                return (matchRatio, "Bad match ratio")
        return (r.status_code, requestJSON)
    else:
        return (r.status_code, "Bad status code")

def getSampleCards():
    #IDs of cards to download
    IDs = [
        "0000579f-7b35-4ed3-b44c-db2a538066fe", # Fury Sliver
        "0000cd57-91fe-411f-b798-646e965eec37", # Siren Lookout
        "0001f1ef-b957-4a55-b47f-14839cdbab6f", # Venerable Knight
        "00020b05-ecb9-4603-8cc1-8cfa7a14befc"  # Wildcall
    ]
    if not os.path.isdir("DemoCards"):
        os.mkdir("DemoCards")
    with open("ExampleCardObjects.json", mode="r") as file:
        demoJSON = json.loads(file.read())
        for entries in demoJSON:
            if entries["id"] in IDs:

                # Download image if it doesn't exist yet
                name = fr"DemoCards/{entries['name']}.jpeg"
                if not os.path.exists(name):

                    try:
                        imageURL = entries["image_uris"]["normal"]
                    except KeyError:
                        print(f"No normal image for {entries['name']}")

                    print(f"Downloading {name}")
                    with urllib.request.urlopen(imageURL) as download:
                        downloadContent = download.read()
                        print(f"Writing file {name}")
                        with open(name, mode="wb") as imageFile:
                            imageFile.write(downloadContent)

                else:
                    print(f"{name} already exists")

                # Make a 180 degree rotated image copy
                if not os.path.exists(f"{name.strip('.jpeg')} Rotated.jpeg"):
                    originalImage = Image.open(name)
                    rotatedImage = originalImage.rotate(180)
                    rotatedImage.save(f"{name.strip('.jpeg')} Rotated.jpeg")
                    print(f"Writing file {name} Rotated")
                else:
                    print(f"{name} Rotated already exists")



def textRecognitionDemo():

    # Get demo images
    images = []
    recognized = []
    for (paths, names, files) in os.walk("DemoCards"):
        print("Input image files:\n", files)
        for i in files:
            images.append(Image.open(f"DemoCards/{i}"))
        break

    for i in images:

        # We need to do some pre image processing to clean them up a bit
        width, height = i.size
        verticalCrop = height / 10

        topCropImage = i.crop((42, 34, width - 120, verticalCrop))
        topCropImage = topCropImage.convert('1') # Convert to black and white
        topCropImage = topCropImage.filter(PIL.ImageFilter.MedianFilter()) # Filter out grainyness

        bottomCropImage = i.crop((124, height - verticalCrop + 2, width - 36, height - 36))
        bottomCropImage = bottomCropImage.convert('1')
        bottomCropImage = bottomCropImage.filter(PIL.ImageFilter.MedianFilter())
        bottomCropImage = bottomCropImage.rotate(180)

        savePathTop = i.filename.replace("DemoCards/", "DemoCards/Temp/")
        savePathTop = savePathTop.replace(".jpeg", "-processed.jpeg")
        savePathBottom = i.filename.replace("DemoCards/", "DemoCards/Temp/")
        savePathBottom = savePathBottom.replace(".jpeg", "-bottom-processed.jpeg")
        if not os.path.isdir("DemoCards/Temp"):
            os.mkdir("DemoCards/Temp")

        topCropImage.save(savePathTop)
        bottomCropImage.save(savePathBottom)

        recognized.append(pytesseract.image_to_string(topCropImage).split('\n')[0])
        recognized.append(pytesseract.image_to_string(bottomCropImage).split('\n')[0])
    print(f"Recognized text from images:\n{recognized}\n")


    return recognized



if __name__ == "__main__":
    #getSampleCards()
    card_titles = textRecognitionDemo()
    for i in card_titles:
        try:
            APILookup = getCardDetails(i)
            if APILookup[0] == 200:
                print()
                print(APILookup[1]['name'])
                print(APILookup[1]['prices'])
                print(json.dumps(APILookup[1], indent=1))
                print()
            else:
                print(f"No API search result for {i}")
        except KeyError:
            pass