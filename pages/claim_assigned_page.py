from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pages.leave_page import LeavePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from dataclasses import dataclass

@dataclass
class ClaimAssignedPage:
    EMP_CLAIMS = (By.XPATH, "//a[normalize-space(.)='Employee Claims']")
    SUCCESS_TOAST = (
        By.XPATH,
        "//div[contains(@class,'oxd-toast') and contains(@class,'oxd-toast--success')]"
    )
    TOAST_CLOSE = (
        By.XPATH,
        "//div[contains(@class,'oxd-toast')]//button[contains(@class,'oxd-toast-close')]"
    )
    USERNAME = (By.XPATH, "//label[normalize-space()='Employee Name']/../..//input")
    SEARCH_BTN = (By.XPATH, "//button[normalize-space()='Search']")

    def __init__(self, driver, wait):

        self.driver = driver
        self.wait = wait

    @staticmethod
    def _group_by_label_xpath(label: str) -> str:
        # scope any control by its label (e.g., "Leave Type", "Employee Name")
        return f"//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{label}']]"
    
    
    def is_success_toast_visible(self, timeout: int = 8) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.SUCCESS_TOAST)
            )
            return True
        except TimeoutException:
            return False

    def close_success_toast(self) -> None:
        # Try clicking the toast's close button; otherwise wait for auto-dismiss
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(self.TOAST_CLOSE)
            ).click()
        except TimeoutException:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.invisibility_of_element_located(self.SUCCESS_TOAST)
                )
            except TimeoutException:
                pass

    
    def open_users_list(self):
        # Use if you aren’t already on Users list page
        self.wait.until(EC.url_contains("/web/index.php/claim/viewAssignClaim"))

    def search_user(self, username) -> bool:
        # type username in filter
        box = self.wait.until(EC.element_to_be_clickable(self.USERNAME))
        box.click()
        box.send_keys(Keys.CONTROL, "a")
        box.send_keys(Keys.DELETE)
        box.send_keys(username)
     # click Search and wait for the table to refresh
        old_body = self.wait.until(EC.presence_of_element_located(self.TABLE_BODY))
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_BTN)).click()
        self.wait.until(EC.staleness_of(old_body))
        self.wait.until(EC.visibility_of_element_located(self.TABLE_BODY))

        # return True iff there’s a row with that exact username
        rows = self.driver.find_elements(*self._row_for_user(username))
        return len(rows) > 0
    
    def click_search(self):
        self.wait.until(EC.element_to_be_clickable(self.EMP_CLAIMS)).click()

    def _row_for_user(self, username: str):
        return (By.XPATH,f"//div[contains(@class,'oxd-table-card')][.//div[normalize-space()='{username}']]")
    
    # def select_employee_autocomplete(self, typed_text: str, option_text: str = None, index: int = 1):
    #     # focus the Employee Name input
    #     inp = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//label[normalize-space()='Employee Name']/../..//input")))
    #     inp.clear()
    #     inp.send_keys(typed_text)