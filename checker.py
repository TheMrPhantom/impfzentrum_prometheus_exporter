from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
import json


def getVacStatus(center):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    print("Headless Firefox Initialized")
    output = None
    for zentrum in range(1, 300):
        driver.get("https://"+"{:03d}".format(zentrum) +
                   "-iz.impfterminservice.de/impftermine/service?plz="+str(center))
        if ("Virtueller Warteraum des Impfterminservice" in driver.page_source):
            print("oh nö")
            continue
        print("Juhu")

        btn = driver.find_elements_by_xpath(
            "//label[@class='ets-radio-control']")[1]
        ActionChains(driver).move_to_element(btn).click(btn).perform()
        driver.implicitly_wait(10)
        driver.get("https://"+"{:03d}".format(zentrum)+"-iz.impfterminservice.de/rest/suche/termincheck?plz="+str(
            center)+"&leistungsmerkmale=L920,L921,L922,L923")
        output = json.loads(driver.find_element_by_xpath(
            "//div[@id='json']").get_attribute("innerHTML"))
        print(center, output)
        break

    driver.quit()
    print("Headless Firefox destructed")
    return output
