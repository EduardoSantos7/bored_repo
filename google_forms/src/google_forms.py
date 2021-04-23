#!/usr/bin/env python

import os
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as expected_conditions

# from utils.postman.postman import send_email


class GoogleForms:

    IDS = {}
    CLASSES = {
        "card_item": "freebirdFormviewerViewNumberedItemContainer",
        "options_container": "freebirdFormviewerComponentsQuestionRadioChoicesContainer",
        "submit": "appsMaterialWizButtonPaperbuttonLabel quantumWizButtonPaperbuttonLabel exportLabel"
    }

    WAIT_ELEMENT = 15

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        self.driver = webdriver.Chrome(
            executable_path="clocker/src/chromedriver", chrome_options=chrome_options)
        self.url_base = "https://docs.google.com/forms/d/e/1FAIpQLSfXYmNvBjRMarKsaqDEJNGrz6LZiYRvG8GCp_mjTQCh5CeBXA/viewform"

    def fill_random(self):
        # Get list of all cards wiith questions
        cards_list = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_all_elements_located(
                (By.CLASS_NAME, self.CLASSES.get('card_item'))
            )
        )

        print(len(cards_list))
        print("---")

        if not cards_list:
            print("No cards with questions")
            return

        for card in cards_list:

            options_container = WebDriverWait(card, self.WAIT_ELEMENT).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, self.CLASSES.get('options_container'))
                )
            )

            options = WebDriverWait(options_container, self.WAIT_ELEMENT).until(
                expected_conditions.presence_of_all_elements_located(
                    (By.TAG_NAME, "span")
                )
            )

            number_of_options = len(options)
            x = random.randint(0, number_of_options - 1)
            options[x].click()
            time.sleep(0.2)

            # check iif requires text if so then pick another option
            while "Esta pregunta es obligatoria." in card.get_attribute('innerHTML'):
                x = random.randint(0, number_of_options - 1)
                options[x].click()
                time.sleep(0.5)

    def process(self):

        self.driver.delete_all_cookies()
        self.driver.get(self.url_base)
        self.fill_random()

        WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                    "span[class*='appsMaterialWizButtonPaperbuttonLabel quantumWizButtonPaperbuttonLabel exportLabel']")
            )
        ).click()

        print("found...")
        time.sleep(5)

        # send_email(f"Error in Clocker: {e}")

        self.driver.close()


for _ in range(70):
    g = GoogleForms()
    g.process()
    time.sleep(1*20)
