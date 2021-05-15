import datetime
from os import lseek, stat, wait
import pytz
import time
import prometheus_client
import checker
import zentren
import os
import envir

# '{"termineVorhanden":true,"vorhandeneLeistungsmerkmale":["L920"]}'


class Main:

    def __init__(self):
        self.metrics = dict()

        self.metrics['impfzentrum_status'] = prometheus_client.Gauge(
            'impfzentrum_status', 'Impfstoffverfügbarkeit', ['zentrum'])
        self.metrics['lasttimechecked'] = prometheus_client.Gauge(
            'impfzentrum_lastCheck', 'Letze prüfung', ['zentrum'])

        self.vac_stations = zentren.getZentren()
        self.vac_checker = checker.Checker()
        self.vac_stations_queue = dict()
        for v in self.vac_stations:
            self.vac_stations_queue[v["PLZ"]] = [v, datetime.datetime.now()]

        prometheus_client.start_http_server(8080)

    def check_stations(self):

        for vac_station_key in self.vac_stations_queue:
            vac_station = self.vac_stations_queue[vac_station_key]
            print(self.check_queue_ready(vac_station[1]))
            if self.check_queue_ready(vac_station[1]):
                result, special = self.vac_checker.getVacStatus(vac_station[0])
                station_label = self.get_station_label(vac_station[0])

                if result is not None:
                    self.valid_response(result, station_label)
                    vac_station[1] = self.create_normal_queue()
                else:
                    self.invalid_response(special, station_label)
                    if special == "warteraum" or special == "telefon" or special == "noservice":
                        vac_station[1] = self.create_timout_queue()
                    else:
                        vac_station[1] = self.create_normal_queue()
                self.update_time_metric(station_label)

                time.sleep(15)

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

    def create_timout_queue(self):
        return datetime.datetime.now()+datetime.timedelta(seconds=envir.timeout)

    def create_normal_queue(self):
        return datetime.datetime.now()+datetime.timedelta(seconds=envir.wait)

    def check_queue_ready(self, time):
        difference = (time-datetime.datetime.now()).total_seconds()

        return difference < 0


main = Main()
while True:
    main.check_stations()
    update_rate = envir.update_rate
    if update_rate is not None:
        time.sleep(int(update_rate))
    else:
        time.sleep(180)
