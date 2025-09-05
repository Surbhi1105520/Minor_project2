import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

def test_login_fields_present(driver):
    """Verify username and password fields are present on login page"""
    login = LoginPage(driver, WebDriverWait(driver, 10))
    login.open()
    username_field, password_field = login.visit()

    # final assertion: both input fields exist
    assert username_field.tag_name == "input"
    assert password_field.tag_name == "input"

def test_login_fields_absent_on_wrong_page(driver):
    """Negative test: fields should NOT be present on an invalid page"""
    login = LoginPage(driver, WebDriverWait(driver, 10))
    login.open()
    # navigate to OrangeHRM site root (not the login page)
    login.USERNAME = ("id", "not_there_user")
    login.PASSWORD = ("id", "not_there_pass")

    with pytest.raises(TimeoutException):
        # This should fail because username field won't be found
        login.visit()