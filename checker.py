import json
import traceback
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import DesiredCapabilities
from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import tor
import datetime
import pytz


def checker_thread(port, center, prometheus_metric):
    url = center["URL"]
    plz = center["PLZ"]
    proxy = tor.Proxy_Handler(port)
    proxy.start_proxy()
    proxy.check_stable_tor_connection()

    profile = FirefoxProfile()
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.set_preference("devtools.jsonview.enabled", False)
    profile.set_preference("general.useragent.override",
                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.socks", "localhost")
    profile.set_preference("network.proxy.socks_port", port)
    profile.update_preferences()

    desired = DesiredCapabilities.FIREFOX
    
    options = Options()
    options.headless = True
    options.add_argument("-devtools")
    ff = None
    modulo = 5
    number_of_tries = 0
    fails = [0, 0]
    responses = [None, None, None, None]
    while True:

        print("Fails: ",fails)
        if fails[0] > 3 or fails[1] > 3:
            proxy.restart_proxy()
            proxy.check_stable_tor_connection()
            
        if number_of_tries % modulo == 0:
            try:
                print("Spawning Firefox")
                if ff is not None:
                    ff.close()
                ff = webdriver.Firefox(
                    options=options, firefox_profile=profile, desired_capabilities=desired)
                ff.set_window_size(1920,1080)
                ff.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                ff.set_page_load_timeout(15)
                print("Loading waiting room")
                ff.get(waiting_room_url(url, plz))
                print("Click cookie button")
                ff.save_screenshot("debug.png")
                wait = webdriver.support.ui.WebDriverWait(ff, 10)
                men_menu = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "(//body//div[@class='app-wrapper']/div[@class='cookies-info']//div[contains(@class,'row')]/div[contains(@class,'text-center')]/div[contains(@class,'row')]//a[contains(@class,'btn')])[1]")))
                webdriver.ActionChains(ff).move_to_element(
                    men_menu).click().perform()
                print("REFRESHED COOKIES")
                print("Waiting for 10 seconds...")
                time.sleep(10)
                fails[0] = 0
            except:
                fails[0] += 1
                traceback.print_exc()
                continue
        else:
            print("Get rest point")
            try:
                ff.get(rest_url(url, plz))
                content_element = ff.find_element_by_xpath("//pre")
                page_content = content_element.get_attribute("innerHTML")

                if "{}" in page_content:
                    print(colored("[CONTENT]: " + page_content, "yellow"))
                else:
                    print(colored("[CONTENT]: " + page_content, "green"))
                page_in_json = json.loads(page_content)
                responses[(number_of_tries % modulo) - 1] = page_in_json
                fails[1] = 0
            except:
                fails[1] += 1
                traceback.print_exc()
        print("Responses: ", responses)
        if (number_of_tries % modulo == 0) and (number_of_tries > 0):
            output = -1
            for response in responses:
                if len(response) == 0:
                    if output != 0:
                        output = 1
                elif response["termineVorhanden"]:
                    output = int(
                        str(response["vorhandeneLeistungsmerkmale"][0]).replace("L", ""))
                    break
                else:
                    output = 0
            print("Respons picked: ", response)
            prometheus_metric[0].labels(
                zentrum=get_station_label(center)).set(output)
            update_time_metric(prometheus_metric[1], get_station_label(center))
            prometheus_metric[1]
        number_of_tries += 1



        time.sleep(5)


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


def invalid_response(metric, special, station_label):
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


def update_time_metric(metric, station_label):
    metric.labels(zentrum=station_label).set(
        datetime.datetime.now(tz=pytz.utc).timestamp()*1000)
