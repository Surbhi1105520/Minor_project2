import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.main_menu_page import MainMenu

# OrangeHRM demo expected routes (SPA)
MENU_TARGETS = [
    ("Dashboard",  "/web/index.php/dashboard"),
    ("Admin",      "/web/index.php/admin"),
    ("PIM",        "/web/index.php/pim"),
    ("Leave",      "/web/index.php/leave"),
    ("Time",       "/web/index.php/time"),
    ("Recruitment","/web/index.php/recruitment"),
    ("My Info",    "/web/index.php/pim/viewPersonalDetails"),
    ("Performance","/web/index.php/performance"),
] 
@pytest.mark.parametrize("menu_text, expected_path", MENU_TARGETS)
def test_main_menu_items_visible_and_functional(driver, menu_text, expected_path):
    wait = WebDriverWait(driver, 10)

    # 1) Login
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # 2) Verify menu item is visible & clickable
    menu = MainMenu(driver, wait)
    assert menu.is_visible(menu_text), f"Menu '{menu_text}' not visible/enabled"

    # 3) Click and verify navigation landed on expected route
    menu.click(menu_text)
    menu.wait_landed(expected_path)

@pytest.mark.negative
def test_menu_item_not_present(driver):
    """
    Negative test:
    Ensure a bogus menu item is NOT visible/clickable.
    """
    wait = WebDriverWait(driver, 10)

    # Login
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # Try to check a non-existent menu item
    menu = MainMenu(driver, wait)
    bogus_item = "NonExistentMenu"
    assert not menu.is_visible(bogus_item), f"❌ Bogus menu '{bogus_item}' should not be visible!"

    
