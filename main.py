import datetime
import pytz
import checker
import zentren
import prometheus_client
# '{"termineVorhanden":true,"vorhandeneLeistungsmerkmale":["L920"]}'
# 429 Derzeit keine onlinebuchung

metrics = dict()

metrics['impfzentrum_status'] = prometheus_client.Gauge(
    'impfzentrum_status', 'Impfstoffverfügbarkeit', ['zentrum'])
metrics['lasttimechecked'] = prometheus_client.Gauge(
    'impfzentrum_lastCheck', 'Letze prüfung', ['zentrum'])

prometheus_client.start_http_server(8080)

vac_stations = zentren.getZentren()
outp = {}

while True:
    for vac_station in vac_stations:
        result, special = checker.getVacStatus(vac_station)
        station_label = vac_station["PLZ"]+"#" + \
            vac_station["Ort"]+"166153284"+vac_station["Zentrumsname"]
        station_label = station_label.strip()
        if result is not None:
            if not result["termineVorhanden"]:
                metrics['impfzentrum_status'].labels(
                    zentrum=station_label).set(0)
            else:
                metrics['impfzentrum_status'].labels(zentrum=station_label).set(
                    int(str(result["vorhandeneLeistungsmerkmale"][0]).replace("L", "")))
        else:
            if special == "warteraum":
                metrics['impfzentrum_status'].labels(
                    zentrum=station_label).set(4)
            elif special == "telefon":
                metrics['impfzentrum_status'].labels(
                    zentrum=station_label).set(3)
            elif special == "noservice":
                metrics['impfzentrum_status'].labels(
                    zentrum=station_label).set(2)
            else:
                metrics['impfzentrum_status'].labels(
                    zentrum=station_label).set(1)
        metrics['lasttimechecked'].labels(zentrum=station_label).set(
            datetime.datetime.now(tz=pytz.utc).timestamp()*1000)
