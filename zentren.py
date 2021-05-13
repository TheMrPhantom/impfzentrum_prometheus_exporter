import json


def getZentren():
    data = None
    with open('zentren.json') as json_file:
        data = json.load(json_file)
    bw = data["Baden-Württemberg"]
    output = list()
    for z in bw:
        if z["PLZ"].startswith("70") or z["PLZ"].startswith("71") or z["PLZ"].startswith("72"):
            output.append(z)
    return output
