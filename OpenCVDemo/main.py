import requests, json, urllib.request, os
from PIL import Image


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


def getSampleCards():
    #IDs of cards to download
    IDs = [
        "0000579f-7b35-4ed3-b44c-db2a538066fe", # Fury Sliver
        "0000a54c-a511-4925-92dc-01b937f9afad", # Spirit
        "0000cd57-91fe-411f-b798-646e965eec37", # Siren Lookout
        "0001f1ef-b957-4a55-b47f-14839cdbab6f", # Venerable Knight
        "00020b05-ecb9-4603-8cc1-8cfa7a14befc"  # Wildcall
    ]
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


if __name__ == "__main__":
    getSampleCards()