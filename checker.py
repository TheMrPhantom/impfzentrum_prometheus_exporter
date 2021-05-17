import json
from random import randint, random
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import tor
import datetime
import pytz
import ChromeChecker


def checker_thread(port, center, prometheus_metric, terminator):

    url = center["URL"]
    plz = center["PLZ"]
    proxy = tor.Proxy_Handler(port)
    proxy.start_proxy()
    proxy.check_stable_tor_connection()

    #desired = DesiredCapabilities.CHROME

    #options = Options()
    #options.headless = True
    # options.add_argument("-devtools")
    ff = None
    modulo = 5
    number_of_tries = 0
    fails = [0, 0]
    responses = [None, None, None, None]
    empty_counter = 0

    print("Starting check loop")

    checker = ChromeChecker.ChromeChecker(port)

    while True:

        output = checker.check_vac(center)
        prometheus_metric[0].labels(
            zentrum=get_station_label(center)).set(output)
        update_time_metric(prometheus_metric[1], get_station_label(center))

        time.sleep(15)
        """
        response=responses[(number_of_tries % modulo) - 1]
        if len(response) == 0:
            output = 1
        elif response["termineVorhanden"]:
            output = int(
                str(response["vorhandeneLeistungsmerkmale"][0]).replace("L", ""))
            break
        else:
            output = 0

        if output == 1:
            empty_counter += 1
        else:
            empty_counter = 0
        print("Respons picked: ", response)
        prometheus_metric[0].labels(
            zentrum=get_station_label(center)).set(output)
        update_time_metric(prometheus_metric[1], get_station_label(center))
        """


def waiting_room_url(url, plz):
    return url+"impftermine/service?plz="+str(plz)


def rest_url(url, plz):
    termin_url = url
    termin_url += "/rest/suche/termincheck?plz="
    termin_url += str(plz)
    termin_url += "&leistungsmerkmale=L920,L921,L922,L923"
    return termin_url


def get_station_label(vac_station):
    station_label = vac_station["PLZ"]
    station_label += "#"
    station_label += vac_station["Ort"]
    station_label += "166153284"
    station_label += vac_station["Zentrumsname"]
    station_label = station_label.strip()

    return station_label


def valid_response(metric, result, station_label):
    if not result["termineVorhanden"]:
        metric.labels(
            zentrum=station_label).set(0)
    else:
        metric.labels(zentrum=station_label).set(
            int(str(result["vorhandeneLeistungsmerkmale"][0]).replace("L", "")))


def update_time_metric(metric, station_label):
    metric.labels(zentrum=station_label).set(
        datetime.datetime.now(tz=pytz.utc).timestamp()*1000)
