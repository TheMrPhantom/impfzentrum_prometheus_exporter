import datetime
from os import stat
import pytz
import time
import prometheus_client
import checker
import zentren
import os
# '{"termineVorhanden":true,"vorhandeneLeistungsmerkmale":["L920"]}'

class Main:

    def __init__(self):
        self.metrics = dict()

        self.metrics['impfzentrum_status'] = prometheus_client.Gauge(
            'impfzentrum_status', 'Impfstoffverfügbarkeit', ['zentrum'])
        self.metrics['lasttimechecked'] = prometheus_client.Gauge(
            'impfzentrum_lastCheck', 'Letze prüfung', ['zentrum'])

        self.vac_stations = zentren.getZentren()
        self.vac_checker=checker.Checker()

        prometheus_client.start_http_server(8080)

    def check_stations(self):

        for vac_station in self.vac_stations:
            result, special = self.vac_checker.getVacStatus(vac_station)
            station_label = self.get_station_label(vac_station)

            if result is not None:
                self.valid_response(result, station_label)
            else:
                self.invalid_response(special, station_label)
            self.update_time_metric(station_label)
            
            time.sleep(27)


    def get_station_label(self, vac_station):
        station_label = vac_station["PLZ"]
        station_label += "#"
        station_label += vac_station["Ort"]
        station_label += "166153284"
        station_label += vac_station["Zentrumsname"]
        station_label = station_label.strip()

        return station_label

    def valid_response(self, result, station_label):
        if not result["termineVorhanden"]:
            self.metrics['impfzentrum_status'].labels(
                zentrum=station_label).set(0)
        else:
            self.metrics['impfzentrum_status'].labels(zentrum=station_label).set(
                int(str(result["vorhandeneLeistungsmerkmale"][0]).replace("L", "")))

    def invalid_response(self, special, station_label):
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

    def update_time_metric(self, station_label):
        self.metrics['lasttimechecked'].labels(zentrum=station_label).set(
            datetime.datetime.now(tz=pytz.utc).timestamp()*1000)


main = Main()
while True:
    main.check_stations()
    update_rate = os.environ.get("UPDATERATE")
    if update_rate is not None:
        time.sleep(int(update_rate))
    else:
        time.sleep(180)
