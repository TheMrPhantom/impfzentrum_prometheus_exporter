import json
from os import name

data = None
with open('zentren.json', encoding='utf8') as json_file:
    data = json.load(json_file)

output=""
for zentr in data:
    if "Baden-" in zentr:
        for z in data[zentr]:
            ort=z["Ort"]
            name=z["Zentrumsname"]

            url = z["URL"]+"impftermine/service?plz="+z["PLZ"]
            output+="* ["+ort+" - "+name+"]("+url+")\n"
        
print(output)

