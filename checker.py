from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver import DesiredCapabilities
import json
import traceback
import signal
import sys
import time
from envir import proxy_port, proxy_hops
import tor


class Checker:

    def __init__(self):
        print("Init browser")

        self.prox = tor.Proxy_Handler()
        self.prox.start_proxy()

        profile = FirefoxProfile()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        profile.update_preferences()

        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", "localhost")
        profile.set_preference("network.proxy.http_port", int(proxy_port))

        desired = DesiredCapabilities.FIREFOX
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options, firefox_profile=profile, desired_capabilities=desired)
        signal.signal(signal.SIGINT, self.kill_signal_handler)
        print("Finished...")

    def kill_signal_handler(self, sig, frame):
        print('SIGINT incoming')
        self.driver.close()
        print('SIGINT processed')
        sys.exit(0)

    def getVacStatus(self, center):
        self.driver.get("http://httpbin.org/ip")
        print(self.driver.page_source)
        url = center["URL"]
        plz = center["PLZ"]
        output = None
        special = None
        for trys in range(0, 2):
            in_waitingroom, waitingroom_text = self.check_in_waitingroom(
                url, plz)
            if in_waitingroom:
                special = waitingroom_text
                continue
            print(trys, "Juhu")
            try:

                page_content = self.check_appointment_page(url, plz)
                if page_content == "{}":
                    print("EmptyPage")
                    self.driver.delete_all_cookies()
                    continue
                output = json.loads(page_content)
                print(plz, output)
                break
            except:
                self.handle_page_error()
                continue
        return output, special

    def check_in_waitingroom(self, url, plz):
        print("\tRefresh page")
        self.driver.refresh()
        time.sleep(15)
        print("\tCall api")
        self.driver.get(url+"impftermine/service?plz="+str(plz))
        special = None
        is_waitingroom = False
        if ("Virtueller Warteraum des Impfterminservice" in self.driver.page_source):
            print("warteraum")
            special = "warteraum"
            is_waitingroom = True
            self.driver.save_screenshot("g.png")

        return is_waitingroom, special

    def click_on_button(self):
        for trys in range(5):
            try:
                radio_xpath = "//label[@class='ets-radio-control']"
                btn = self.driver.find_elements_by_xpath(radio_xpath)[0]
                ActionChains(self.driver).move_to_element(
                    btn).click(btn).perform()

                radio_xpath = "//label[@class='ets-radio-control']"
                btn = self.driver.find_elements_by_xpath(radio_xpath)[1]
                ActionChains(self.driver).move_to_element(
                    btn).click(btn).perform()
                break
            except:
                pass

    def check_appointment_page(self, url, plz):
        termin_url = url
        termin_url += "/rest/suche/termincheck?plz="
        termin_url += str(plz)
        termin_url += "&leistungsmerkmale=L920,L921,L922,L923"
        self.driver.get(termin_url)
        div_xpath = "//div[@id='json']"
        content_element = self.driver.find_element_by_xpath(div_xpath)
        page_content = content_element.get_attribute("innerHTML")

        print("Rest Endpoint Loaded")

        return page_content

    def handle_page_error(self):

        self.driver.save_screenshot("fail.png")
        output = None
        if "wenden Sie sich bitte telefonisch" in self.driver.page_source:
            output = "telefon"
            print("Telefon")
        elif "Derzeit keine Onlinebuchung von Impfterminen" in self.driver.page_source:
            output = "noservice"
            print("No_Service")
        else:
            traceback.print_exc()
            print("Error after base page")

        return output
