import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.main_menu_page import MainMenu
from pages.my_info_page import MyInfoPage

MY_INFO_TABS = [
    ("Personal Details",   "/web/index.php/pim/viewPersonalDetails"),
    ("Contact Details",    "/web/index.php/pim/viewContactDetails"),
    ("Emergency Contacts", "/web/index.php/pim/viewEmergencyContacts"),
    ("Dependents",         "/web/index.php/pim/viewDependents"),
    ("Immigration",        "/web/index.php/pim/viewImmigration"),
    ("Job",                "/web/index.php/pim/viewJobDetails"),
    ("Salary",             "/web/index.php/pim/viewSalaryList"),
    ("Report-to",          "/web/index.php/pim/viewReportToDetails"),
    ("Qualifications",     "/web/index.php/pim/viewQualifications"),
    ("Memberships",        "/web/index.php/pim/viewMemberships"),
]

@pytest.mark.parametrize("menu_text, expected_path", MY_INFO_TABS)
def test_my_info_tabs_visible_and_functional_positive(driver, menu_text, expected_path):
    wait = WebDriverWait(driver, 15)

    # 1) Login
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # 2) Navigate to My Info from the LEFT sidebar (use MainMenu, not DashboardPage)
    main = MainMenu(driver, wait)
    assert main.is_visible("My Info"), "My Info not visible in sidebar"
    main.click("My Info")
    wait.until(EC.url_contains("/web/index.php/pim/"))  # will include empNumber query param

    # 3) Verify and click each My Info tab
    myinfo = MyInfoPage(driver, wait)
    assert myinfo.is_tab_visible(menu_text), f"'{menu_text}' tab not visible/enabled"
    myinfo.click_tab(menu_text)
    myinfo.wait_landed(menu_text, expected_path)


@pytest.mark.negative
def test_my_info_tabs_negative(driver):
    wait = WebDriverWait(driver, 15)

    # 1) Login
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # 2) Navigate to My Info from LEFT sidebar
    main = MainMenu(driver, wait)
    assert main.is_visible("My Info", timeout=5), "My Info not visible in sidebar"
    main.click("My Info")

    # 3) Wait for My Info to load (URL + tab container visible)
    wait.until(EC.url_contains("/web/index.php/pim/"))
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//div[contains(@class,'orangehrm-tabs') or contains(@class,'orangehrm-edit-employee')]"
    )))
    # Optional: dismiss loaders/backdrops if your app shows them
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".oxd-loading-spinner, .oxd-overlay, .oxd-backdrop"))
        )
    except Exception:
        pass

    # 4) Negative: bogus tab must NOT be visible
    myinfo = MyInfoPage(driver, wait)
    bogus = "NonExistentTab"
    assert not myinfo.is_tab_visible(bogus, timeout=2), f"❌ Bogus tab '{bogus}' should not be visible!"
