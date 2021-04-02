import os
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as expected_conditions

from utils.postman.postman import send_email


class Clocker:

    IDS = {
        'user_box': 'txtUserName',
        "pass_box": 'txtPassword',
        "login_button": 'loginIn',
        "push_in_button": "ContentPlaceHolder1_lbPunchInDis",
        "push_out_button": "ContentPlaceHolder1_lbPunchOut",
        "action_notification": "lblPunchNotification"
    }
    WAIT_ELEMENT = 15

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = False
        self.driver = webdriver.Chrome(
            executable_path="clocker/src/chromedriver", chrome_options=chrome_options)
        self.url_base = "https://app1.trackmytime.com/onestar"

    def login(self):
        # Login
        user_box = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.ID, self.IDS.get('user_box'))
            )
        )

        pass_box = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.ID, self.IDS.get('pass_box'))
            )
        )

        login_button = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.ID, self.IDS.get('login_button'))
            )
        )

        user_box.clear()
        user_box.send_keys(os.getenv('CLOCKER_USER'))
        pass_box.clear()
        pass_box.send_keys(os.getenv('CLOCKER_PASS'))
        login_button.click()

    def toggle_status(self):
        """If we are logged in then log out or vice versa
        """
        try:
            push_in_button = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, self.IDS.get('push_in_button'))
                )
            )

            if push_in_button.isEnabled():
                logging.info("Push In button is enabled, let's push in")
                push_in_button.click()
                return

        except TimeoutException as e:
            logging.error(e)

        try:
            push_out_button = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, self.IDS.get('push_out_button'))
                )
            )

            if push_out_button.isEnabled():
                logging.info("Push Out button is enabled, let's push in")
                push_out_button.click()
                return

        except TimeoutException as e:
            logging.error(e)

    def get_message(self):
        try:
            action_notification = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, self.IDS.get('action_notification'))
                )
            )

            return action_notification.text.strip()

        except TimeoutException as e:
            logging.error(e)

    def process(self):
        try:
            self.driver.get(self.url_base)

            self.login()
            self.toggle_status()

            message = self.get_message()

            send_email(message)
        except Exception as e:
            logging.error(e)
