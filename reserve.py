import os
import selenium
import selenium.webdriver
import subprocess
import sys
import time

from datetime import date
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
from selenium.webdriver.common.by import By

# This should be in local storage on the browser when you login
# Application->Local Storage->https://recreation.gov->recaccount (copy full json)
ACCOUNT_INFO=os.getenv("ACCOUNT_INFO")
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

    script = "localStorage.setItem('recaccount', '{}');".format(ACCOUNT_INFO)

    driver.execute_script(script)

    driver.get(REC_URL)

    now = datetime.now()
    tomorrow_date = now + timedelta(days=1)
    if tomorrow:
        curr_hour = now.hour
        # Assumes tickets are released at 8am and 11am in same timezone
        h = 11 if abs(11-curr_hour) < abs(8-curr_hour) else 8
        print("closer to:", h)
        wait_until = datetime(now.year, now.month, now.day, h)
        print("waiting until", wait_until)
        loop = 0
        while datetime.now() < wait_until:
            if loop % 15 == 0:
                print("still waiting...")
            time.sleep(0.1)
            loop += 1

    print("let's gooooo")

    reserved = reload_and_reserve(driver, tomorrow_date, tomorrow)
    if not reserved:
        if tomorrow:
            while not reserved:
                time.sleep(1)
                print("Trying again")
                reserved = reload_and_reserve(driver, tomorrow_date, tomorrow)
        else:
            while True:
                time.sleep(1)
    else:
        while True:
            print("BOOK IT!!")
            time.sleep(10)


def reload_and_reserve(driver, tomorrow_date, tomorrow):
    driver.get(REC_URL)

    input_element = driver.find_element(By.XPATH, "//input[@name='tourCalendarWithKey']")

    desired_date = tomorrow_date.strftime("%m/%d/%Y") if tomorrow else "04/10/2022"
    print("booking for", desired_date)
    input_element.send_keys(desired_date)

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
        if 'reservation' in driver.current_url:
           break
        try:
           reserve_button = driver.find_element(By.XPATH, '//*[@id="page-content"]/main/div[2]/div/div[1]/div[1]/div/div[3]/div[2]/button')
           reserve_button.click()
        except Exception:
            continue


    maybe_cart = driver.current_url
    if 'reservation' in maybe_cart:
        cart_quantity = driver.find_elements(By.XPATH, "//span[@class='cart-quantity']")
        if len(cart_quantity) > 0:
            print("you have", cart_quantity[0].text, "reservations")
            return True
        else:
            print("you have no reservations")
            return False
    else:
        print("you have no reservations")
        return False

if __name__ == "__main__":
    load_dotenv()
    ACCOUNT_INFO=os.getenv("ACCOUNT_INFO")

    book_rainforest(len(sys.argv) > 1)
