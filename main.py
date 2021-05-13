import datetime
from os import stat
import pytz
import checker
import zentren
import prometheus_client
# '{"termineVorhanden":true,"vorhandeneLeistungsmerkmale":["L920"]}'
# 429 Derzeit keine onlinebuchung


class Main:

    def __init__(self):
        self.metrics = dict()

        self.metrics['impfzentrum_status'] = prometheus_client.Gauge(
            'impfzentrum_status', 'Impfstoffverfügbarkeit', ['zentrum'])
        self.metrics['lasttimechecked'] = prometheus_client.Gauge(
            'impfzentrum_lastCheck', 'Letze prüfung', ['zentrum'])

        self.vac_stations = zentren.getZentren()

        prometheus_client.start_http_server(8080)

    def check_stations(self):

        for vac_station in self.vac_stations:
            result, special = checker.getVacStatus(vac_station)
            station_label = vac_station["PLZ"]+"#" + \
                vac_station["Ort"]+"166153284"+vac_station["Zentrumsname"]
            station_label = station_label.strip()
            if result is not None:
                if not result["termineVorhanden"]:
                    self.metrics['impfzentrum_status'].labels(
                        zentrum=station_label).set(0)
                else:
                    self.metrics['impfzentrum_status'].labels(zentrum=station_label).set(
                        int(str(result["vorhandeneLeistungsmerkmale"][0]).replace("L", "")))
            else:
                if special == "warteraum":
                    self.metrics['impfzentrum_status'].labels(
                        zentrum=station_label).set(4)
                elif special == "telefon":
                    self.metrics['impfzentrum_status'].labels(
                        zentrum=station_label).set(3)
                elif special == "noservice":
                    self.metrics['impfzentrum_status'].labels(
                        zentrum=station_label).set(2)
                else:
                    self.metrics['impfzentrum_status'].labels(
                        zentrum=station_label).set(1)
            self.metrics['lasttimechecked'].labels(zentrum=station_label).set(
                datetime.datetime.now(tz=pytz.utc).timestamp()*1000)

    def get_station_label(self, vac_station):
        station_label = vac_station["PLZ"]
        station_label += "#"
        station_label += vac_station["Ort"]
        station_label += "166153284"
        station_label += vac_station["Zentrumsname"]
        station_label = station_label.strip()

        return station_label
