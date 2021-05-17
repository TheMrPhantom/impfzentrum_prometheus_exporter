import subprocess
import envir
import time
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import InvalidSessionIdException

import envir
from selenium import webdriver
from termcolor import colored
import datetime
import json
import traceback

class Proxy_Handler:
    
    def __init__(self,proxy_port=None):
        self.proc=None
        if proxy_port is None:
            proxy_port=envir.proxy_port

        self.port=proxy_port   
        self.profile = FirefoxProfile()
        self.profile.set_preference("dom.webdriver.enabled", False)
        self.profile.set_preference('useAutomationExtension', False)  
        self.profile.set_preference("devtools.jsonview.enabled", False)  

        self.profile.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        self.profile.update_preferences()

        self.profile.set_preference("network.proxy.type", 1)
        self.profile.set_preference("network.proxy.socks", "localhost")
        self.profile.set_preference("network.proxy.socks_port", int(proxy_port))

        self.desired = DesiredCapabilities.FIREFOX
        self.options = Options()
        self.options.headless = True

        self.options.add_argument("-devtools")

        self.driver = webdriver.Firefox(
            options=self.options, firefox_profile=self.profile, desired_capabilities=self.desired)
        


    def start_proxy(self,output=False):
        # with output to console
        print("Start tor connection")
        if output:
            self.proc = subprocess.Popen(['torpy_socks', '-p', str(self.port), '--hops', str(envir.proxy_hops)])
        else:
            self.proc = subprocess.Popen(['torpy_socks', '-p', str(self.port), '--hops', str(envir.proxy_hops)],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for i in range(6):
            #print("sleeping",i,"/","6")
            time.sleep(1)
        print("Done connecting")
    
    def stop_proxy(self):
        try:
            self.proc.terminate()
            return True
        except:
            return False
    
    def restart_proxy(self,output=False):
        self.stop_proxy()
        self.start_proxy(output)

    def check_stable_tor_connection(self, output=False):
        connection_stable = False
        ip_found = None
        while not connection_stable:
            try:
                self.restart_proxy(output)
                self.driver.get("http://api.ipify.org?format=json")
                self.driver.save_screenshot("connection.png")
                div_xpath = "//pre"
                content_element = self.driver.find_element_by_xpath(div_xpath)
                page_content = content_element.get_attribute("innerHTML")
                if ip_found != page_content:
                    print(colored(datetime.datetime.now(), "yellow"))
                ip_found = json.loads(page_content)
                print("\t", colored(page_content, "yellow"))
                connection_stable = True
            except InvalidSessionIdException:
                self.driver.close() 
                self.driver = webdriver.Firefox(
                options=self.options, firefox_profile=self.profile, desired_capabilities=self.desired)  
            except:
                time.sleep(0.5)
                traceback.print_exc()
                print(colored("No stable tor connection", "red"))
        return ip_found['ip']