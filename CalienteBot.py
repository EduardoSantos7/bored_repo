import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as expected_conditions


class CalienteBot:
    WAIT_ELEMENT = 20
    XPATHS = {
        'MX_fut': '//*[@id="nav-area"]/div[3]/ul/li[1]/a',
        'user_box': '//*[@id="header-area"]/div[2]/div[1]/form/div[1]/label[1]/input',
        "pass_box": '//*[@id="header-area"]/div[2]/div[1]/form/div[2]/label/input',
        "login_button": '//*[@id="header-area"]/div[2]/div[1]/form/li/input'
    }

    def __init__(self):
        # chrome_options = Options()
        # Getchrome_options.headless = False
        self.driver = webdriver.Chrome(
            executable_path="./chromedriver")
        self.url_base = 'https://sports.caliente.mx/es_MX'

    def _read_web(self):
        # Get page
        self.driver.get(self.url_base)

        # Login
        user_box = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, self.XPATHS.get('user_box'))
            )
        )

        pass_box = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, self.XPATHS.get('pass_box'))
            )
        )

        login_button = WebDriverWait(self.driver, self.WAIT_ELEMENT).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, self.XPATHS.get('login_button'))
            )
        )

        user_box.clear()
        user_box.send_keys()
        pass_box.clear()
        pass_box.send_keys()
        login_button.click()

        time.sleep(5)


CalienteBot()._read_web()
