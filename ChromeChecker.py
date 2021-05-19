from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common.exceptions import InvalidElementStateException, TimeoutException
from selenium.webdriver import DesiredCapabilities
import random
from termcolor import colored
import datetime
import paho.mqtt.client as mqtt
import envir
import threading
import json


class ChromeChecker:

    def __init__(self, proxy_port=None):
        self.init_mqtt()
        self.proxy_port = proxy_port

    def open_browser(self):
        print("Browser open")
        for i in range(5):
            try:
                capabilities = DesiredCapabilities.CHROME

                self.driver = webdriver.Chrome(
                    options=self.get_chrome_options(self.proxy_port), desired_capabilities=capabilities)
                self.wait = WebDriverWait(self.driver, 25)
                return
            except:
                pass
        raise InvalidElementStateException

    def close_browser(self):
        self.driver.close()

    def get_chrome_options(self, proxy_port=None):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')
        chrome_options.add_argument("user-data-dir=chro/")
        chrome_options.add_argument("window-size=1280,800")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")

        if proxy_port is not None:
            chrome_options.add_argument(
                "--proxy-server=socks5://localhost:" + str(proxy_port))
        return chrome_options

    def print_logs(self):
        logs_raw = self.driver.get_log("performance")
        logs = [self.json.loads(lr["message"])["message"] for lr in logs_raw]

        for log in filter(self.log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            print(f"Caught {resp_url}")
            print(self.driver.execute_cdp_cmd(
                "Network.getResponseBody", {"requestId": request_id}))

    def log_filter(self, log_):
        return (
            # is an actual response
            log_["method"] == "Network.responseReceived"
            # and json
            and "json" in log_["params"]["response"]["mimeType"]
        )

    def check_vac(self, center):
        self.open_browser()
        # Make more undetectable
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.get(center["URL"])
        time.sleep(10)
        start_url = center["URL"]+"impftermine/service?plz="+center["PLZ"]

        self.driver.get(start_url)
        self.driver.save_screenshot("1.png")
        print("Mainpage loaded")

        # Warteraum check is "Virtueller Warteraum des Impfterminservice" if warteraum
        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//h1')))

        webpage_info = title.text
        print(colored("[Page]", "yellow"), "\t", webpage_info)
        if webpage_info == "Virtueller Warteraum des Impfterminservice":
            print(colored("In waiting room", "cyan"))
            return 4

        print("No waiting room")

        try:
            button = self.driver.find_element_by_xpath(
                '//a[contains(text(),"Auswahl bestätigen")]')
            button.click()
            self.driver.save_screenshot("2.png")
            print("Cookies needed to be accepted")
        except:
            print("Cookies already accepted")
            pass

        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH,
                '//input[@type="radio" and @name="vaccination-approval-checked"]//following-sibling::span[contains(text(),"Nein")]/..')))
        element.click()
        time.sleep(random.randint(2, 4))
        self.driver.save_screenshot("3.png")
        print("Clicked on 'No' button")

        vaccine_available = False
        output = -1
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "alert-danger")]')))
            vaccine_available = not ('keine freien Termine' in element.text)
            print(colored("[Page]", "yellow"), "\t", element.text)
            # self.print_logs()
            self.driver.save_screenshot(
                "images/"+center["PLZ"]+"-"+str(datetime.datetime.now())+".png")
            if "Gehören Sie einer impfberechtigten Personengruppen an?" in self.driver.page_source:
                output = 7
            if "Bitte geben Sie Ihr Alter ein" in self.driver.page_source:
                output = 8
            if "impfberechtigten" in self.driver.page_source:
                output = 9

        except TimeoutException:
            print(colored("Maybe vaccine available", "magenta"))
            output = 5
        self.driver.get(center["URL"]+"rest/suche/termincheck?plz=" +
                        center["PLZ"]+"&leistungsmerkmale=L920,L921,L922,L923")
        time.sleep(15)
        rest = self.driver.page_source
        f = open("images/"+center["PLZ"]+"-" +
                 str(datetime.datetime.now())+".txt", "w")
        f.write(rest)
        f.close()

        self.close_browser()

        if "{}" in rest:
            return -1

        print("Vaccine available:", vaccine_available)
        if output != -1:
            return output

        if vaccine_available:
            output = 6
            print(colored("Vaccine available", "green"))
        else:
            print(colored("No vaccine available", "magenta"))
            output = 0

        return output

    def init_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(envir.broker_adress, 1883, 60)
        thread = threading.Thread(target=self.loop, daemon=True)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    def loop(self):
        while True:
            self.client.loop()
            time.sleep(1)

    def publish(self, string_to_publish):
        self.client.publish(envir.mqtt_topic, string_to_publish, qos=1)
