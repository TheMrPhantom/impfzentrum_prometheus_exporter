import time
import datetime
import pytz
import checker
import os

#'{"termineVorhanden":true,"vorhandeneLeistungsmerkmale":["L920"]}'

import prometheus_client

plz=["73730","71065","71297","71334","71636"]

metrics=dict()

metrics['impfzentrum_status']=prometheus_client.Gauge('impfzentrum_status', 'Impfstoffverfügbarkeit',['zentrum'])
metrics['lasttimechecked']=prometheus_client.Gauge('impfzentrum_lastCheck', 'Letze prüfung',['zentrum'])

prometheus_client.start_http_server(int(os.environ.get('PORT')))

plz=["73730","71065","71297","71334","71636"]
outp={}
while True:
    for p in plz:
        result=checker.getVacStatus(p)
        if result is not None:
            if not result["termineVorhanden"]:
                metrics['impfzentrum_status'].labels(zentrum=p).set(0)
            else:
                metrics['impfzentrum_status'].labels(zentrum=p).set(int(str(result["vorhandeneLeistungsmerkmale"][0]).replace("L","")))
        else:
            metrics['impfzentrum_status'].labels(zentrum=p).set(429)
        metrics['lasttimechecked'].labels(zentrum=p).set(datetime.datetime.now(tz=pytz.utc).timestamp()*1000)
