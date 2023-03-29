import json
import requests
#item type weapon = 3

API_ROOT = "https://www.bungie.net/Platform/Destiny2/"
CONTENT_ROOT = "https://www.bungie.net"
API_KEY = "89c9db2c0a8b46449bb5e654b6e594d0"  # no yoinky😡
API_KEY_HEADER = {"X-API-Key": API_KEY}

manifest = requests.get(API_ROOT + "Manifest/", headers=API_KEY_HEADER).json()
contentPaths = manifest["Response"]["jsonWorldComponentContentPaths"]["en"]
itemData:dict[str, dict] = requests.get(CONTENT_ROOT + contentPaths["DestinyInventoryItemDefinition"], headers=API_KEY_HEADER).json()

data = {}

WEAPON_STAT_HASHES = set([
    1591432999,
    1345609583,
    3614673599,
    447667954,
    943549884,
    1931675084,
    3871231066,
    1240592695,
    2715839340,
    4188031367,
    1842278586,
    155624089,
    2523465841,
    3555269338
])
    
for key in itemData:
    value = itemData[key]
    hash = int(key)
    if not (value["itemType"] == 3 and value["inventory"]["tierType"] == 5):
        continue
    intrinsic_hash = value["sockets"]["socketEntries"][0]["singleInitialItemHash"]
    if int(intrinsic_hash) not in data:
        data[int(intrinsic_hash)] = {}
    for stat in value["investmentStats"]:
        if not stat["statTypeHash"] in WEAPON_STAT_HASHES:
            continue
        try:
            data_pointer = data[int(intrinsic_hash)]
            if stat["value"] < data_pointer[int(stat["statTypeHash"])][0]:
                buf_tuple = (stat["value"],data_pointer[int(stat["statTypeHash"])][1])
                data_pointer[int(stat["statTypeHash"])] = buf_tuple
            elif stat["value"] > data_pointer[int(stat["statTypeHash"])][1]:
                buf_tuple = (data_pointer[int(stat["statTypeHash"])][0], stat["value"],)
                data_pointer[int(stat["statTypeHash"])] = buf_tuple
        except KeyError:
            stat_val = stat["value"]
            buf_tuple = (stat_val, stat_val)
            data[int(intrinsic_hash)][int(stat["statTypeHash"])] = buf_tuple
with open("./whatever.json", "w") as f:
    json.dump(data, f,indent=4)




print(data)
    
    