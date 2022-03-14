import subprocess
from pathlib import Path

import selenium
import selenium.webdriver
from selenium.webdriver.common.by import By
import sys
import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import sys
ACCOUNT_INFO=""

REC_URL = "https://www.recreation.gov/ticket/300017/ticket/3020"


def book_rainforest(tomorrow=False):
    options = selenium.webdriver.chrome.options.Options()
    options.add_argument("start-maximized")

    node_modules_bin = subprocess.run(
        ["npm", "bin"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        check=True
    )
    node_modules_bin_path = node_modules_bin.stdout.strip()
    chromedriver_path = Path(node_modules_bin_path) / "chromedriver"

    # service = selenium.webdriver.chrome.service.Service(chromedriver_path)
    # service.start()
    # driver = selenium.webdriver.Remote(service.service_url, options=options)
    driver = selenium.webdriver.Chrome(
        options=options,
        executable_path=str(chromedriver_path),
    )

    driver.get(REC_URL)

    # TODO: log in to recreation.gov, and set account_info equal to value associated w/ recaccount key in Local Storage.
    # Store it as a string. It should start with {"access token": ....
    script = "localStorage.setItem('recaccount', '{}');".format(ACCOUNT_INFO)

    driver.execute_script(script)

    driver.get(REC_URL)

    now = datetime.now()
    tomorrow_date = now + timedelta(days=1)
    if tomorrow:
        curr_hour = now.hour
        h = 11 if abs(11-curr_hour) < abs(8-curr_hour) else 8
        print("closer to:", h)
        wait_until = datetime(tomorrow_date.year, tomorrow_date.month, tomorrow_date.day, h)
        print(wait_until)
        while datetime.now() < wait_until:
            time.sleep(0.1)

    print("let's gooooo")

    reserved = reload_and_reserve(driver, tomorrow_date, tomorrow)
    if tomorrow and not reserved:
        while not reserved:
            time.sleep(1)
            print("Trying again")
            reserved = reload_and_reserve(driver, tomorrow_date, tomorrow)


def reload_and_reserve(driver, tomorrow_date, tomorrow):
    driver.get(REC_URL)

    input_element = driver.find_element(By.XPATH, "//input[@name='tourCalendarWithKey']")

    # TODO: Set the date in MM/DD/YYYY format
    desired_date = tomorrow_date.strftime("%m/%d/%Y") if tomorrow else "03/31/2022"
    input_element.send_keys(desired_date)

    time_slot = []
    while len(time_slot) == 0:
        time_slot = driver.find_elements(By.XPATH, "//input[@type='radio']")
    pill = []
    while len(pill) == 0:
        pill = driver.find_elements(By.XPATH, "//div[@class='ti-radio-pill']")
    print("selected", len(pill), "radio buttons")


    for slot in pill:
       print("reserving!")
       action = selenium.webdriver.common.action_chains.ActionChains(driver)
       action.move_to_element(slot)
       action.click()
       action.perform()
       reserve_button = driver.find_element(By.XPATH, '//*[@id="page-content"]/main/div[2]/div/div[1]/div[1]/div/div[3]/div[2]/button')
       reserve_button.click()

    cart_quantity = driver.find_elements(By.XPATH, "//span[@class='cart-quantity']")
    print(len(cart_quantity))
    if len(cart_quantity) > 0:
        print("you have", cart_quantity[0].text, "reservations")
        return True
    else:
        print("you have no reservations")
        return False





if __name__ == "__main__":
    book_rainforest(len(sys.argv) > 1)


