import requests, json, urllib.request, time, os
from PIL import Image


"""

    Example entry
    {
    "object":"card",
    "id":"0000579f-7b35-4ed3-b44c-db2a538066fe",
    "oracle_id":"44623693-51d6-49ad-8cd7-140505caf02f",
    "multiverse_ids":[109722],
    "mtgo_id":25527,
    "mtgo_foil_id":25528,
    "tcgplayer_id":14240,
    "cardmarket_id":13850,
    "name":"Fury Sliver",
    "lang":"en",
    "released_at":"2006-10-06",
    "uri":"https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe",
    "scryfall_uri":"https://scryfall.com/card/tsp/157/fury-sliver?utm_source=api",
    "layout":"normal",
    "highres_image":true,
    "image_status":"highres_scan",
    "image_uris":
        {
        "small":"https://c1.scryfall.com/file/scryfall-cards/small/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "normal":"https://c1.scryfall.com/file/scryfall-cards/normal/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "large":"https://c1.scryfall.com/file/scryfall-cards/large/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "png":"https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
        "art_crop":"https://c1.scryfall.com/file/scryfall-cards/art_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "border_crop":"https://c1.scryfall.com/file/scryfall-cards/border_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979"
    },
    "mana_cost":"{5}{R}",
    "cmc":6.0,
    "type_line":"Creature — Sliver",
    "oracle_text":"All Sliver creatures have double strike.",
    "power":"3",
    "toughness":"3",
    "colors":["R"],
    "color_identity":["R"],
    "keywords":[],
    "legalities":{"standard":"not_legal","future":"not_legal","historic":"not_legal","gladiator":"not_legal","pioneer":"not_legal","modern":"legal","legacy":"legal","pauper":"not_legal","vintage":"legal","penny":"legal","commander":"legal","brawl":"not_legal","historicbrawl":"not_legal","paupercommander":"restricted","duel":"legal","oldschool":"not_legal","premodern":"not_legal"},
    "games":["paper","mtgo"],
    "reserved":false,
    "foil":true,
    "nonfoil":true,
    "finishes":["nonfoil","foil"],
    "oversized":false,
    "promo":false,
    "reprint":false,
    "variation":false,
    "set_id":"c1d109bc-ffd8-428f-8d7d-3f8d7e648046",
    "set":"tsp",
    "set_name":"Time Spiral",
    "set_type":"expansion",
    "set_uri":"https://api.scryfall.com/sets/c1d109bc-ffd8-428f-8d7d-3f8d7e648046",
    "set_search_uri":"https://api.scryfall.com/cards/search?order=set\u0026q=e%3Atsp\u0026unique=prints",
    "scryfall_set_uri":"https://scryfall.com/sets/tsp?utm_source=api",
    "rulings_uri":"https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe/rulings",
    "prints_search_uri":"https://api.scryfall.com/cards/search?order=released\u0026q=oracleid%3A44623693-51d6-49ad-8cd7-140505caf02f\u0026unique=prints",
    "collector_number":"157",
    "digital":false,
    "rarity":"uncommon",
    "flavor_text":"\"A rift opened, and our arrows were abruptly stilled. To move was to push the world. But the sliver's claw still twitched, red wounds appeared in Thed's chest, and ribbons of blood hung in the air.\"\n—Adom Capashen, Benalish hero",
    "card_back_id":"0aeebaf5-8c7d-4636-9e82-8c27447861f7",
    "artist":"Paolo Parente",
    "artist_ids":["d48dd097-720d-476a-8722-6a02854ae28b"],
    "illustration_id":"2fcca987-364c-4738-a75b-099d8a26d614",
    "border_color":"black",
    "frame":"2003",
    "full_art":false,
    "textless":false,
    "booster":true,
    "story_spotlight":false,
    "edhrec_rank":5230,
    "prices":
    {
        "usd":"0.45","usd_foil":"2.04","usd_etched":null,"eur":"0.19","eur_foil":"4.99","tix":"0.02"
    },
    "related_uris":{"gatherer":"https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=109722","tcgplayer_infinite_articles":"https://infinite.tcgplayer.com/search?contentMode=article\u0026game=magic\u0026partner=scryfall\u0026q=Fury+Sliver\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall","tcgplayer_infinite_decks":"https://infinite.tcgplayer.com/search?contentMode=deck\u0026game=magic\u0026partner=scryfall\u0026q=Fury+Sliver\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall","edhrec":"https://edhrec.com/route/?cc=Fury+Sliver","mtgtop8":"https://mtgtop8.com/search?MD_check=1\u0026SB_check=1\u0026cards=Fury+Sliver"}
    },

"""

def compress_images(quality = 90):
    dir_list = os.listdir("Images/")
    space_saved = 0
    average = 0
    num = 0
    for files in dir_list:
        file_name = f"Images/{files}"
        current_size = os.path.getsize(file_name)
        image = Image.open(file_name)
        image.save(file_name, optimize = True, quality = quality)
        new_size = os.path.getsize(file_name)
        current_space_saved = current_size - new_size
        space_saved = space_saved + current_space_saved
        num = num + 1
        average = space_saved / num
        print(f"Compressed {file_name} saved {current_space_saved}")
    print(f"Average {average}")
    print(f"Total {space_saved}")





def download_cards():
    print("Reading cards json file...")
    with open("all-cards-20211013091057.json", mode="r") as f:
        data = json.load(f)
        f.close()

    print("Start gathering images")
    for entries in data:
        if entries["object"] == "card" and entries["lang"] == "en":
            if entries["image_status"] != "missing":
                name = entries["name"].replace("\\", "")
                name = name.replace("/", "")
                file_name = fr"Images/{name}.jpg"
                if not os.path.exists(file_name):
                    try:
                        image_url = entries["image_uris"]["small"]
                    except KeyError:
                        print(f"Could not get small image for {entries['name']}")
                        continue
                    print(f"Downloading image {image_url}")
                    time.sleep(0.1)
                    with urllib.request.urlopen(image_url) as f:
                        img = f.read()

                        print(f"Writing file {file_name}")
                        with open(file_name, mode="wb") as out_file:
                            out_file.write(img)
                else:
                    print(f"{file_name} already exists")

if __name__ == "__main__":
    """
    r = requests.get("https://api.scryfall.com/bulk-data")
    print(r.status_code)
    print(r.encoding)
    with open("bulk-data.json", mode="w") as f:
        j = json.loads(r.text)
        t = json.dumps(j, indent=4)
        f.write(t)
    """
    compress_images(85)


