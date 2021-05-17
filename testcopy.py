from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver import DesiredCapabilities
from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
profile = FirefoxProfile()
profile.set_preference("dom.webdriver.enabled", False)
profile.set_preference('useAutomationExtension', False)  
profile.set_preference("devtools.jsonview.enabled", False)  
profile.set_preference("general.useragent.override",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
profile.update_preferences()

desired = DesiredCapabilities.FIREFOX
options = Options()
options.headless = True
options.add_argument("-devtools")

modulo=5
number_of_tries=0
fmodulo = 5
while True:
    if number_of_tries % modulo == 0:
        ff = webdriver.Firefox(options=options, firefox_profile=profile, desired_capabilities=desired)
        ff.get("https://229-iz.impfterminservice.de/impftermine/service?plz=88367")
        wait = webdriver.support.ui.WebDriverWait(ff, 10)
        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "(//body//div[@class='app-wrapper']/div[@class='cookies-info']//div[contains(@class,'row')]/div[contains(@class,'text-center')]/div[contains(@class,'row')]//a[contains(@class,'btn')])[1]")))
        webdriver.ActionChains(ff).move_to_element(men_menu).click().perform()
        print("REFRESHED COOKIES")
        time.sleep(10)
    else:
        ff.get(
            "https://229-iz.impfterminservice.de/rest/suche/termincheck?plz=88367&leistungsmerkmale=L920,L921,L922,L923")
        site_content = ff.page_source
        print("[CONTENT]" + site_content)

    number_of_tries += 1
    time.sleep(2)









