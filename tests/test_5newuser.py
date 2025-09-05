import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.main_menu_page import MainMenu
from pages.admin_users_page import AdminUsersPage
from pages.login_page import LoginPage
from pages.header_bar import HeaderBar
from selenium.webdriver.common.by import By

def test_create_user_and_validate_login(driver):
    wait = WebDriverWait(driver, 15)

    # Login as Admin
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # Go to Admin → Users
    menu = MainMenu(driver, wait)
    menu.click("Admin")
    wait.until(EC.url_contains("/web/index.php/admin"))

    # Add a unique user (use a strong password to satisfy policy)
    username = f"autouser_{int(time.time())%100000}"
    password = "Passw0rd!"
    admin = AdminUsersPage(driver, wait)
    admin.add_user(
        employee_name_hint="Rah",      # what you type
        employee_exact="Rahul Das",    # which suggestion to click; or omit to pick 1st
        username=username,
        password=password,
        user_role="Admin",
        status="Enabled",
    )

    # OPTIONAL: verify dashboard after logging in with the new user
    hdr = HeaderBar(driver, wait)
    hdr.logout()
    wait.until(EC.url_contains("/auth/login"))

    login.login(username, password)
    wait.until(EC.url_contains("/web/index.php/dashboard"))
    assert wait.until(EC.visibility_of_element_located((By.XPATH, "//h6[normalize-space()='Dashboard']")))

def test_add_user_without_selecting_employee_shows_validation_error(driver):
    wait = WebDriverWait(driver, 15)

    # 1) Login as Admin
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # 2) Go to Admin → Users
    menu = MainMenu(driver, wait)
    menu.click("Admin")
    wait.until(EC.url_contains("/web/index.php/admin"))

    # 3) Open Add User form
    admin = AdminUsersPage(driver, wait)
    admin.open_add_form()

    # 4) Fill required fields BUT purposely DO NOT select Employee from suggestions
    admin._select_dropdown("User Role", "ESS")
    admin._type_input("Employee Name", "rah")  # type only, don't pick suggestion
    admin._select_dropdown("Status", "Enabled")

    username = f"neguser_{int(time.time())%100000}"
    password = "Passw0rd!"
    admin._type_input("Username", username)
    admin._type_input("Password", password)
    admin._type_input("Confirm Password", password)

    # 5) Try to Save
    wait.until(EC.element_to_be_clickable(AdminUsersPage.SAVE_BTN)).click()

    # 6) Assert validation error under Employee Name
    emp_error = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//label[normalize-space()='Employee Name']/../..//span[contains(@class,'oxd-input-field-error-message')]"
    )))
    assert emp_error.is_displayed(), "Expected validation error under 'Employee Name'"

    # 7) Assert we are still on the Add form (not navigated back to list)
    assert "/web/index.php/admin/saveSystemUser" in driver.current_url, \
        "Form should not submit when Employee Name is not selected from suggestions"
