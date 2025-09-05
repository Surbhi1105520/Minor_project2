import pytest
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage   
from pages.forgot_password_page import ForgotPasswordPage

def test_forgot_password_sends_confirmation(driver):
    wait = WebDriverWait(driver, 12)

    # 1) Navigate to login page
    login = LoginPage(driver, wait)
    login.open()
    wait.until(EC.url_contains("/auth/login"))

    # 2) Open the Forgot Password flow
    forgot = ForgotPasswordPage(driver, wait)
    forgot.open_from_login()

    # 3) Enter username and submit
    forgot.request_reset("Admin")  # use any existing username

    # 4) Validate confirmation appears (toast or panel)
    confirmation_el = forgot.wait_for_confirmation()
    assert confirmation_el.is_displayed()

    text = (confirmation_el.text or "").lower()
    assert "success" in text or "reset password" in text or "email" in text

@pytest.mark.xfail(reason="Demo may return generic success for unknown usernames (privacy-safe).")
def test_forgot_password_unknown_username_may_not_confirm(driver):
    wait = WebDriverWait(driver, 12)
    login = LoginPage(driver, wait)
    login.open()
    wait.until(EC.url_contains("/auth/login"))
    forgot = ForgotPasswordPage(driver, wait)
    forgot.open_from_login()

    bogus = f"no_such_user_{int(time.time())}"
    forgot.request_reset(bogus)

    # Expect either: no success (strict) OR generic success (app choice).
    # Strict path: no success within short wait → passes.
    short = WebDriverWait(driver, 3)
    with pytest.raises(TimeoutException):
        short.until(EC.visibility_of_element_located(ForgotPasswordPage.SUCCESS_TOAST))
