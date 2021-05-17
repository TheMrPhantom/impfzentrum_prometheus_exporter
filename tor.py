import subprocess
import envir
import time
from selenium.webdriver import ActionChains
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import InvalidSessionIdException


from selenium.webdriver.chrome.options import Options


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
        self.proxy_port=proxy_port
        self.spawn_chrome()
    
    def spawn_chrome(self):
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

        if self.proxy_port is not None:
             chrome_options.add_argument("--proxy-server=socks5://localhost:" + str(self.proxy_port));
        self.driver = webdriver.Chrome(options=chrome_options)
        

    def start_proxy(self,output=False):
        # with output to console
        print("Start tor connection")
        if output:
            self.proc = subprocess.Popen(['torpy_socks', '-p', str(self.proxy_port), '--hops', str(envir.proxy_hops)])
        else:
            self.proc = subprocess.Popen(['torpy_socks', '-p', str(self.proxy_port), '--hops', str(envir.proxy_hops)],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
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
                self.spawn_chrome()
            except:
                time.sleep(0.5)
                traceback.print_exc()
                print(colored("No stable tor connection", "red"))
        return ip_found['ip']