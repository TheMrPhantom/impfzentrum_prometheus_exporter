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


for i in range(20):
    browser = webdriver.Firefox(
    options=options, firefox_profile=profile, desired_capabilities=desired)
    try:
        browser.get("https://229-iz.impfterminservice.de/impftermine/service?plz=71065")

        wait = WebDriverWait(browser, 10)
        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "(//body//div[@class='app-wrapper']/div[@class='cookies-info']//div[contains(@class,'row')]/div[contains(@class,'text-center')]/div[contains(@class,'row')]//a[contains(@class,'btn')])[1]")))
        ActionChains(browser).move_to_element(men_menu).click().perform()

        browser.get("https://229-iz.impfterminservice.de/rest/suche/termincheck?plz=71065&leistungsmerkmale=L920,L921,L922,L923")

        wait = WebDriverWait(browser, 10)
        men_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "//pre")))
        ActionChains(browser).move_to_element(men_menu).click().perform()

        print(browser.page_source)
    except:
        print("Error")
    finally:
        browser.close()










"""
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

cook=browser.get_cookies()
cookie_param=dict()

for coo in cook:
    cookie_param[coo['name']]= coo['value']

with open(datetime.now()., 'a') as f:
    print(var, file=f)

for i in range(10):
    a=requests.get("https://229-iz.impfterminservice.de/rest/suche/termincheck?plz=71065&leistungsmerkmale=L920,L921,L922,L923",cookies=cookie_param,headers=header)

print(a.text,a.reason)
"""