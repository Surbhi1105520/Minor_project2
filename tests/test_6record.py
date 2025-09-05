# tests/test_user_listing.py
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.main_menu_page import MainMenu
from pages.admin_users_page import AdminUsersPage
from pages.header_bar import HeaderBar


@pytest.fixture
def go_to_users_page(driver):
    """Login as Admin and land on Admin → User Management → Users list."""
    wait = WebDriverWait(driver, 15)
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))
    menu = MainMenu(driver, wait)
    menu.click("Admin")
    wait.until(EC.url_contains("/web/index.php/admin/viewSystemUsers"))
    return wait


def test_user_listing_positive(driver, go_to_users_page):
    """
    Positive: create a new system user, then verify it appears in Users list.
    """
    wait = go_to_users_page
    admin = AdminUsersPage(driver, wait)
    # Create a unique user (pick first matching employee from autocomplete)
    username = f"autouser_{int(time.time())%100000}"
    password = "Passw0rd!"
    admin.add_user(
        employee_name_hint="Rah",     # type 'P' and pick the first suggestion internally
        employee_exact="Rahul Das",
        username=username,
        password=password,
        user_role="Admin",
        status="Enabled",
        # If your add_user supports employee_exact=..., you can pass that too
    )

    # Validate presence in Users grid
    admin.open_users_list()  # no-op if already on list
    assert admin.search_user(username) is True, f"New user '{username}' not found in Users list"

def test_user_listing_negative(driver, go_to_users_page):
    """
    Negative: try to 'create' a user WITHOUT selecting Employee Name from suggestions.
    The form should not submit; the user should not appear in the Users list.
    """
    wait = go_to_users_page
    admin = AdminUsersPage(driver, wait)
    # Open Add User form directly
    admin.open_add_form()
    # Fill fields BUT do NOT select employee from autocomplete (type only)
    admin._select_dropdown("User Role", "ESS")
    admin._type_input("Employee Name", "rah")  # <-- no suggestion click
    admin._select_dropdown("Status", "Enabled")
    bad_username = f"neguser_{int(time.time())%100000}"
    password = "Passw0rd!"
    admin._type_input("Username", bad_username)
    admin._type_input("Password", password)
    admin._type_input("Confirm Password", password)
    # Attempt to save
    wait.until(EC.element_to_be_clickable(AdminUsersPage.SAVE_BTN)).click()
    # Expect a validation error under Employee Name and remain on the add form
    emp_error = wait.until(EC.visibility_of_element_located((By.XPATH,"//label[normalize-space()='Employee Name']/../..//span[contains(@class,'oxd-input-field-error-message')]")))
    assert emp_error.is_displayed(), "Expected validation error under 'Employee Name'"
    assert "/web/index.php/admin/saveSystemUser" in driver.current_url, \
"Form should not submit if Employee Name wasn't selected from suggestions"

    # Navigate back to Users list and confirm the bogus username is NOT present
    menu = MainMenu(driver, wait)
    menu.click("Admin")
    wait.until(EC.url_contains("/web/index.php/admin/viewSystemUsers"))

    assert admin.search_user(bad_username) is False, \
        f"Did not expect '{bad_username}' to appear in Users list"
