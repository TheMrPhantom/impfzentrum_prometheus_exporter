from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
import json
import time

print("Init browser")
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

print("Finished...")

def getVacStatus(center):
    

    url = center["URL"]
    plz = center["PLZ"]
    output = None
    special = None
    for trys in range(1, 5):
        driver.get(url+"impftermine/service?plz="+str(plz))
        if ("Virtueller Warteraum des Impfterminservice" in driver.page_source):
            print("warteraum")
            special = "warteraum"
            driver.save_screenshot("g.png")

            continue
        print(trys, "Juhu")
        try:

            btn = driver.find_elements_by_xpath(
                "//label[@class='ets-radio-control']")[1]
            ActionChains(driver).move_to_element(btn).click(btn).perform()
            print("PageLoaded")
            time.sleep(10)
            driver.get(url+"/rest/suche/termincheck?plz="+str(
                plz)+"&leistungsmerkmale=L920,L921,L922,L923")
                
            page_content = driver.find_element_by_xpath(
                "//div[@id='json']").get_attribute("innerHTML")
            print("RestLoaded")
            if page_content == "{}":
                print("EmptyPage")
                continue
            output = json.loads(page_content)
            print(plz, output)
            break
        except:
            print("catched")
            driver.save_screenshot("fail.png")
            if "wenden Sie sich bitte telefonisch" in driver.page_source:
                special = "telefon"
            if "Derzeit keine Onlinebuchung von Impfterminen" in driver.page_source:
                special = "noservice"
            continue

    return output, special
