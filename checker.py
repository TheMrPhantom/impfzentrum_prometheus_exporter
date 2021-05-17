import time
import tor
import datetime
import pytz
import ChromeChecker


def checker_thread(port, center, prometheus_metric, terminator):

    proxy = tor.Proxy_Handler(port)
    proxy.start_proxy()
    proxy.check_stable_tor_connection()

    print("Starting check loop")
    try:
        checker = ChromeChecker.ChromeChecker(port)

        while True:

            output = checker.check_vac(center)
            prometheus_metric[0].labels(
                zentrum=get_station_label(center)).set(output)
            update_time_metric(prometheus_metric[1], get_station_label(center))

            time.sleep(15)
    except:
        terminator()


def get_station_label(vac_station):
    station_label = vac_station["PLZ"]
    station_label += "#"
    station_label += vac_station["Ort"]
    station_label += "166153284"
    station_label += vac_station["Zentrumsname"]
    station_label = station_label.strip()

    return station_label


def update_time_metric(metric, station_label):
    metric.labels(zentrum=station_label).set(
        datetime.datetime.now(tz=pytz.utc).timestamp()*1000)
