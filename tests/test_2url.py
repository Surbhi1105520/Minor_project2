import pytest
from selenium.common.exceptions import WebDriverException,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage

LOGIN_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"


def test_url_positive(driver):
    # create page object
    visit = LoginPage(driver, WebDriverWait(driver, 10))
    

    
def test_url_negative(driver):
    login = LoginPage(driver, WebDriverWait(driver, 10))
    login.open()
    assert driver.current_url != "https://example.com/wrong-url"

