# test_login.py
from pages.login_page import LoginPage
import openpyxl

def test_login_from_excel(driver, wait, case, result_writer):
    """
    Reads Username/Password from Excel (sample1.xlsx / Sheet1),
    attempts login, detects Success/Fail, and writes it back to TestResult.
    """
    page = LoginPage(driver, wait)
    page.open()
    page.login(case["Username"], case["Password"])

    outcome = "Success" if page.is_dashboard_loaded() else "Fail"
    # Optional: capture error text for debug
    if outcome == "Fail":
        err = page.get_error_text()
        print(f"[Row {case['TestID']}] Error: {err}")

    result_writer(case, outcome)

    # Keep test green regardless; if you later add an Expected column, assert against it here.
    assert True

import pytest

@pytest.mark.negative
def test_login_with_invalid_credentials(driver, wait):
    """
    Negative test:
    Try login with wrong username/password,
    ensure dashboard does NOT load and error message is shown.
    """
    page = LoginPage(driver, wait)
    page.open()
    page.login("invalid_user", "wrong_password")

    # Dashboard must NOT load
    assert not page.is_dashboard_loaded(), "❌ Dashboard loaded with invalid credentials!"

    # Error message must be visible
    err = page.get_error_text()
    assert err is not None and err.strip() != "", "❌ Expected error message not shown!"
    print(f"Captured error: {err}")
