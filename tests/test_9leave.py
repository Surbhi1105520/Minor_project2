import datetime as dt
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.main_menu_page import MainMenu
from pages.leave_page import LeavePage
from pages.assignleave_page import AssignLeavePage

#@pytest.mark.smoke
def test_assign_leave_and_verify_in_records_positive(driver):
    wait = WebDriverWait(driver, 15)
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # Go to Leave → Assign Leave
    menu = MainMenu(driver, wait)
    assert menu.is_visible("Leave", timeout=5)
    menu.click("Leave")
    wait.until(EC.url_contains("/web/index.php/leave/"))
    leave = LeavePage(driver, wait)
    leave.open_assign_leave()
    assert leave.assign_leave_landed()
    # Fill the form
    assignleave = AssignLeavePage(driver, wait)
    assignleave._select_dropdown_by_label("Leave Type", "CAN - Bereavement")
    assignleave.select_employee_autocomplete(typed_text="Rah", option_text="Rahul Das")
    # Dates (tomorrow, single day)
    assignleave.set_from_date("2025-09-01")
    assignleave.set_to_date("2025-09-02")
    # Assign
    assignleave._click_assign()


@pytest.mark.negative
def test_assign_leave_without_employee_shows_validation_error(driver):
    wait = WebDriverWait(driver, 15)

    # Login
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # Go to Leave → Assign Leave
    menu = MainMenu(driver, wait)
    assert menu.is_visible("Leave", timeout=5)
    menu.click("Leave")
    wait.until(EC.url_contains("/web/index.php/leave/"))

    leave = LeavePage(driver, wait)
    leave.open_assign_leave()
    assert leave.assign_leave_landed()

    # Fill everything EXCEPT Employee Name
    assignleave = AssignLeavePage(driver, wait)
    assignleave._select_dropdown_by_label("Leave Type", "CAN - Bereavement")

    start = dt.date.today() + dt.timedelta(days=1)
    day = start.strftime("%Y-%m-%d")
    assignleave.set_from_date(day)
    assignleave.set_to_date(day)

    # Optional: ensure duration is set
    try:
        assignleave._select_dropdown_by_label("Duration", "Full Day")
    except Exception:
        pass

    # Click Assign (handles confirm modal if it appears)
    assignleave._click_assign()

    # Expect inline validation under Employee Name
    err_locator = (
        By.XPATH,
        LeavePage._group_by_label_xpath("Employee Name")
        + "//span[contains(@class,'oxd-input-field-error-message')]"
    )
    err = wait.until(EC.visibility_of_element_located(err_locator))
    assert (err.text or "").strip().lower() in {"required", "invalid"}

    # Ensure no success toast appeared
    success_toasts = driver.find_elements(
        By.XPATH, "//div[contains(@class,'oxd-toast') and contains(@class,'oxd-toast--success')]"
    )
    assert not any(t.is_displayed() for t in success_toasts), "Unexpected success toast when Employee Name is missing"
    


    # toast = leave.assign_leave(
    #     employee_hint="Rah",
    #     employee_exact="Rahul Das",
    #     leave_type="CAN - Personal",
    #     from_date=from_date,
    #     to_date=to_date,
    #     duration="Full Day",
    #     comment="Automated assignment",
    # )
    # assert toast.is_displayed()
    # assert any(k in (toast.text or "").lower() for k in ("success", "assigned"))

    # # Verify in Leave List
    # leave.open_leave_list()
    # leave.filter_leave_list("Rah", "Rahul Das", from_date, to_date)
    # assert leave.has_result_row_for_date(from_date, to_date)


# @pytest.mark.negative
# def test_assign_leave_without_employee_negative(driver):
#     wait = WebDriverWait(driver, 15)

#     # Login (no chaining)
#     login = LoginPage(driver, wait)
#     login.open()
#     login.login("Admin", "admin123")
#     wait.until(EC.url_contains("/web/index.php/dashboard"))

#     # Go to Leave → Assign Leave
#     menu = MainMenu(driver, wait)
#     assert menu.is_visible("Leave", timeout=5)
#     menu.click("Leave")
#     wait.until(EC.url_contains("/web/index.php/leave/"))

#     leave = LeavePage(driver, wait)
#     leave.open_assign_leave()

#     # Fill everything EXCEPT Employee Name
#     start = dt.date.today() + dt.timedelta(days=1)
#     from_date = start.strftime("%Y-%m-%d")
#     to_date   = start.strftime("%Y-%m-%d")

#     leave._select_dropdown_by_label("Leave Type", "CAN - Personal")
#     leave._set_date_by_label("From Date", from_date)
#     leave._set_date_by_label("To Date", to_date)
#     leave._select_dropdown_by_label("Duration", "Full Day")

#     # Click Assign
#     wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Assign']"))).click()

#     # Expect inline validation under Employee Name
#     error_locator = (
#         By.XPATH,
#         LeavePage._group_by_label_xpath("Employee Name")
#         + "//span[contains(@class,'oxd-input-field-error-message')]"
#     )
#     err = wait.until(EC.visibility_of_element_located(error_locator))
#     assert (err.text or "").strip().lower() in ("required", "invalid"), f"Unexpected error text: {err.text}"

#     # Ensure no success toast
#     toasts = driver.find_elements(By.CSS_SELECTOR, ".oxd-toast, .oxd-toast-content")
#     assert not any(t.is_displayed() for t in toasts), "Unexpected success toast when Employee Name is missing"
