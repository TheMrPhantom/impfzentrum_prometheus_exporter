from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common.exceptions import TimeoutException
import random
from termcolor import colored

class ChromeChecker:

    def __init__(self, proxy_port=None):
        self.driver = webdriver.Chrome(
            options=self.get_chrome_options(proxy_port))
        self.wait = WebDriverWait(self.driver, 25)
        print("Browser open")

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

    def check_vac(self, center):
        # Make more undetectable
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        start_url = center["URL"]+"impftermine/service?plz="+center["PLZ"]

        self.driver.get(start_url)
        self.driver.save_screenshot("1.png")
        print("Mainpage loaded")

        # Warteraum check is "Virtueller Warteraum des Impfterminservice" if warteraum
        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//h1')))
        webpage_info = title.text
        if webpage_info == "Virtueller Warteraum des Impfterminservice":
            print(colored("In waiting room","cyan"))
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
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "alert-danger")]')))
            vaccine_available = not ('keine freien Termine' in element.text)
        except TimeoutException:
            print(colored("Maybe vaccine available","magenta"))
            return 5

        self.driver.save_screenshot("4.png")

        print("Vaccine available:", vaccine_available)

        output = -1
        if vaccine_available:
            output = 6
            print(colored("Vaccine available","green"))
        else:
            print(colored("No vaccine available","magenta"))
            output = 0

        return output
