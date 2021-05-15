import json
import os
from random import randint


def getZentren():
    data = None
    with open('zentren.json') as json_file:
        data = json.load(json_file)
    bw = data["Baden-Württemberg"]
    output, debug = list(), list()
    for z in bw:
        if z["PLZ"].startswith("70") or z["PLZ"].startswith("71") or z["PLZ"].startswith("72") or z["PLZ"] == "73730" or z["PLZ"] == "75175":
            output.append(z)
        else:
            debug.append(z)

    debug_mode = os.environ.get("DEBUG")
    if debug_mode is None or debug_mode == 0:
        return output
    else:
        one_random_impfzentrum = debug[randint(0, len(debug)-1)]
        debug_output = list()
        debug_output.append(one_random_impfzentrum)
        return debug_output
