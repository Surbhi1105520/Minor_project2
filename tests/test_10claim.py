import datetime as dt
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage
from pages.main_menu_page import MainMenu
from pages.claim_page import ClaimPage
from pages.assignclaim_page import AssignClaimPage
from pages.claim_assigned_page import ClaimAssignedPage

@pytest.mark.smoke
def test_claim_positive(driver):
    wait = WebDriverWait(driver, 15)
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # Go to Claim → Assign Claim
    menu = MainMenu(driver, wait)
    assert menu.is_visible("Claim", timeout=5)
    menu.click("Claim")
    wait.until(EC.url_contains("/web/index.php/claim/viewAssignClaim"))
    claim = ClaimPage(driver, wait)
    claim._assign_claim()
    
    
    # OnassignClaim
    assignclaim = AssignClaimPage(driver, wait)
    assignclaim.select_employee_autocomplete(typed_text="Ja", option_text="James Butler")
    assignclaim.select_event("Accommodation")
    assignclaim.select_currency("Algerian Dinar")

    
    wait.until(EC.element_to_be_clickable(AssignClaimPage.CREATE_BTN)).click()
    assignclaim.close_success_toast()
    #assigned.click(ClaimAssignedPage.EMP_CLAIMS)
    assigned = ClaimAssignedPage(driver, wait)
    wait.until(EC.url_contains("/web/index.php/claim/assignClaim/id/"))
    assigned.click_search()
    claim.open_users_list()
    assert claim.search_user("James Butler"), "Created claim not found in Employee Claims list"


@pytest.mark.negative
def test_assign_claim_without_event_negative(driver):
    wait = WebDriverWait(driver, 15)

    # Login
    login = LoginPage(driver, wait)
    login.open()
    login.login("Admin", "admin123")
    wait.until(EC.url_contains("/web/index.php/dashboard"))

    # Claim → Assign Claim
    menu = MainMenu(driver, wait)
    assert menu.is_visible("Claim", timeout=5)
    menu.click("Claim")
    wait.until(EC.url_contains("/web/index.php/claim/viewAssignClaim"))
    ClaimPage(driver, wait)._assign_claim()
    wait.until(EC.url_contains("/web/index.php/claim/assignClaim"))

    # Fill only Employee + Currency (INTENTIONALLY skip Event)
    assign = AssignClaimPage(driver, wait)
    assign.select_employee_autocomplete(typed_text="Ja", option_text="James Butler")
    assign.select_currency("Algerian Dinar")

    # Try to create
    url_before = driver.current_url
    wait.until(EC.element_to_be_clickable(AssignClaimPage.CREATE_BTN)).click()

    # 1) Inline validation under Event
    event_error = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='Event']]"
        "//span[contains(@class,'oxd-input-field-error-message') or normalize-space()='Required']"
    )))
    assert event_error.is_displayed(), "Expected 'Required' validation under Event."

    # 2) No success toast
    try:
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class,'oxd-toast') and contains(@class,'oxd-toast--success')]"
        )))
        assert False, "Unexpected success toast; claim should not be created without Event."
    except TimeoutException:
        pass

    # 3) Still on Assign Claim (and NOT on an id page)
    url_after = driver.current_url
    assert "/web/index.php/claim/assignClaim" in url_after, \
        f"Should remain on Assign Claim; got {url_after}"
    assert "/web/index.php/claim/assignClaim/id/" not in url_after, \
        f"Should not navigate to assigned claim id page; got {url_after}"

    # 4) Create button still present (form not submitted)
    wait.until(EC.visibility_of_element_located(AssignClaimPage.CREATE_BTN))
