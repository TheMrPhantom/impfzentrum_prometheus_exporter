from datetime import date, datetime
from os import lseek
from warnings import catch_warnings
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
from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random


class Checker:

    def __init__(self, ip_function=None):
        print("Init browser")

        self.ip_function = ip_function
        self.prox = tor.Proxy_Handler()
        print("Proxy initial start")
        self.prox.start_proxy()
        print("Proxy initial start done")

        profile = FirefoxProfile()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)  
        profile.set_preference("devtools.jsonview.enabled", False)  

        profile.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        profile.update_preferences()

        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", "localhost")
        profile.set_preference("network.proxy.socks_port", int(proxy_port))

        desired = DesiredCapabilities.FIREFOX
        options = Options()
        options.headless = True

        options.add_argument("-devtools")

        self.driver = webdriver.Firefox(
            options=options, firefox_profile=profile, desired_capabilities=desired)
        signal.signal(signal.SIGINT, self.kill_signal_handler)

        """
        self.driver.get("https://001-iz.impfterminservice.de/impftermine/service?plz=70376")
        self.get_cookie_number(self.driver.get_cookie("akavpau_User_allowed"))
        time.sleep(1.654)
        self.driver.get("https://001-iz.impfterminservice.de/rest/suche/termincheck?plz=70376&leistungsmerkmale=L920,L921,L922,L923")
        print("{}" not in self.driver.page_source)
        self.get_cookie_number(self.driver.get_cookie("akavpau_User_allowed"))
        time.sleep(1)
        self.driver.get("https://001-iz.impfterminservice.de/rest/suche/termincheck?plz=70376&leistungsmerkmale=L920,L921,L922,L923")
        print("{}" not in self.driver.page_source)
        self.get_cookie_number(self.driver.get_cookie("akavpau_User_allowed"))
        time.sleep(1)
        self.driver.get("https://001-iz.impfterminservice.de/rest/suche/termincheck?plz=70376&leistungsmerkmale=L920,L921,L922,L923")
        print("{}" not in self.driver.page_source)
        self.get_cookie_number(self.driver.get_cookie("akavpau_User_allowed"))
        time.sleep(1)
        self.driver.get("https://001-iz.impfterminservice.de/rest/suche/termincheck?plz=70376&leistungsmerkmale=L920,L921,L922,L923")
        print("{}" not in self.driver.page_source)
        self.get_cookie_number(self.driver.get_cookie("akavpau_User_allowed"))
        self.driver.get("https://001-iz.impfterminservice.de/rest/suche/termincheck?plz=70376&leistungsmerkmale=L920,L921,L922,L923")
        print("{}" not in self.driver.page_source)
        """
        print("Finished...")


    def make_stable_tor_connection(self, output=False):
        connection_stable = False
        ip_found = None
        while not connection_stable:
            try:
                self.prox.restart_proxy(output)
                self.driver.get("http://api.ipify.org?format=json")
                self.driver.save_screenshot("connection.png")
                div_xpath = "//pre"
                content_element = self.driver.find_element_by_xpath(div_xpath)
                page_content = content_element.get_attribute("innerHTML")
                if ip_found != page_content:
                    print(colored(datetime.now(), "yellow"))
                ip_found = json.loads(page_content)
                print("\t", colored(page_content, "yellow"))
                connection_stable = True
                
            except:
                time.sleep(0.5)
                traceback.print_exc()
                print(colored("No stable tor connection", "red"))
        return ip_found['ip']

    def get_cookie_number(self, cookie):
        cook = cookie["value"]
        tilde_pos = cook.find("~")
        print(cook[:tilde_pos], cook[tilde_pos+4:])


    def kill_signal_handler(self, sig, frame):
        print('SIGINT incoming')
        self.driver.close()
        print('SIGINT processed')
        sys.exit(0)

    def getVacStatus(self, center):

        url = center["URL"]
        plz = center["PLZ"]

        ip = self.make_stable_tor_connection()
        self.ip_function(ip, center)
        print("Load base page")
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "(//body//div[@class='app-wrapper']//div[contains(@class,'d-flex')]/div[@class='page-ets']/div[@class='container']//div[contains(@class,'row')]/div[contains(@class,'offset-1')]/form[contains(@class,'ng-untouched')]/div[contains(@class,'form-group')])[4]")))
            ActionChains(self.driver).move_to_element(men_menu).click().perform()
        except:
            pass
        print("Done")


        output = None
        special = None
        
        in_waitingroom, waitingroom_text = self.check_in_waitingroom(
            url, plz)
        if in_waitingroom:
            special = waitingroom_text
            return output, special
        try:
            self.click_on_button()
            page_content = self.check_appointment_page(url, plz)
            if page_content == "{}":
                print("EmptyPage")
                self.driver.delete_all_cookies()
                return output, special
            output = json.loads(page_content)
            print(plz, output)
            return output, special
        except:
            self.handle_page_error()
            return output, special

    def check_in_waitingroom(self, url, plz):
        print("Check if in waiting room")
        self.driver.get(url+"impftermine/service?plz="+str(plz))
        try:
            wait = WebDriverWait(self.driver, 10)
            men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "(//body//div[@class='app-wrapper']/div[@class='cookies-info']//div[contains(@class,'row')]/div[contains(@class,'text-center')]/div[contains(@class,'row')]//a[contains(@class,'btn')])[1]")))
            ActionChains(self.driver).move_to_element(men_menu).click().perform()
        except:
            print("No cookie button")
        self.driver.save_screenshot("mainpage.png")
        special = None
        is_waitingroom = False
        if ("Virtueller Warteraum des Impfterminservice" in self.driver.page_source):
            print("warteraum")
            special = "warteraum"
            is_waitingroom = True
        else:
            print("Done")

        return is_waitingroom, special

    def click_on_button(self):

        print("Click on button")

        wait = WebDriverWait(self.driver, 10)
        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "(//body//div[@class='app-wrapper']//div[contains(@class,'d-flex')]/div[@class='page-ets']/div[@class='container']//div[contains(@class,'row')]/div[contains(@class,'offset-1')]//div[contains(@class,'row')]//div//span)[2]")))
        ActionChains(self.driver).move_to_element(men_menu).click().perform()
        print("Done")
        self.driver.save_screenshot("btn_click.png")



    def check_appointment_page(self, url, plz):
        termin_url = url
        termin_url += "/rest/suche/termincheck?plz="
        termin_url += str(plz)
        termin_url += "&leistungsmerkmale=L920,L921,L922,L923"
        self.driver.get(termin_url)
        div_xpath = "//pre"
        
        for i in range(5):

            try:
                print(self.driver.page_source)
                print("Checking availablility",i,datetime.now())
                self.driver.save_screenshot(str(i)+".png")
                wait = WebDriverWait(self.driver, 20)
                men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, div_xpath)))
                ActionChains(self.driver).move_to_element(men_menu).click().perform()
                print("Done",datetime.now())
                print(self.driver.page_source)
                print("Trying to read availability from page")
                content_element = self.driver.find_element_by_xpath(div_xpath)
                page_content = content_element.get_attribute("innerHTML")
                print(colored(page_content,"yellow"))
                self.driver.save_screenshot("rest.png")
                print("Done")
                if "{}" in page_content:
                    self.driver.refresh()
                    continue
                break
            except:
                self.driver.refresh()

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
            print("Error")

        return output

    def get_waiting_time(self):
        t = ((int(random.random()*100)/10.0)/2)+5
        print("Waiting for", t, "seconds...")
        return t
