import requests
import json
import time
#'{"termineVorhanden":true,"vorhandeneLeistungsmerkmale":["L920"]}'

import prometheus_client

plz=["73730","71065","71297","71334","71636"]

metrics=dict()

metrics['impfzentrum_status']=prometheus_client.Gauge('impfzentrum_status', 'Impfstoffverfügbarkeit',['zentrum'])

prometheus_client.start_http_server(8004)

plz=["73730","71065","71297","71334","71636"]
outp={}
while True:
    for zentrum in range(1,300):
        for p in plz:
            session = requests.Session()
            session.get("https://"+"{:03d}".format(zentrum)+"-iz.impfterminservice.de/impftermine/service?plz="+p,headers={"Referer":"https://"+"{:03d}".format(zentrum)+"-iz.impfterminservice.de/impftermine/service?plz="+p,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"})
            r=session.get("https://"+"{:03d}".format(zentrum)+"-iz.impfterminservice.de/rest/suche/termincheck?plz="+p+"&leistungsmerkmale=L920,L921,L922,L923",headers={"Referer":"https://"+"{:03d}".format(zentrum)+"-iz.impfterminservice.de/impftermine/service?plz="+p,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"})
            print(r,r.text)
            if r.status_code != 200:
                outp[p]=r.status_code
            else:
                resp=json.loads(r.text)
                if r.text=="{}":
                    print("empty")
                    outp[p]=0
                    continue
                if resp["termineVorhanden"]:
                    for m in resp["vorhandeneLeistungsmerkmale"]:
                        outp[p]=int(resp["vorhandeneLeistungsmerkmale"].replace("L",""))
                else:
                    outp[p]=0
            
        print(outp)
        print()

        for p in plz:
            metrics['impfzentrum_status'].labels(zentrum=p).set(outp[p])
        time.sleep(30)


