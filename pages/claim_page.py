from dataclasses import dataclass
from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@dataclass
class ClaimPage:
    ASS_BTN = (By.XPATH, "//button[normalize-space(.)='Assign Claim']")
    EMPLOYEE_NAME_INPUT = (
        By.XPATH,
        "//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='Employee Name']]//input"
    )
    SEARCH_BTN = (By.XPATH, "//button[normalize-space()='Search']")
    TABLE_BODY = (By.CSS_SELECTOR, ".oxd-table-body")
    EMPLOYEE_CLAIMS_TAB = (By.XPATH, "//header//nav//a[normalize-space()='Employee Claims']")
    

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def _assign_claim(self) -> None:
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space(.)='Assign Claim']")
        )).click()
        self.wait.until(EC.url_contains("/web/index.php/claim/assignClaim"))

    @staticmethod
    def _group_by_label_xpath(label: str) -> str:
        # wrapper for any field group that contains this label
        return f"//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{label}']]"


    # ------------ basic field helpers ------------
    def _input_by_label(self, label: str) -> WebElement:
        el = self.wait.until(EC.presence_of_element_located((By.XPATH, self._group_by_label_xpath(label) + "//input")))
        self._scroll_into_view(el)
        return el

    def _textarea_by_label(self, label: str) -> WebElement:
        el = self.wait.until(EC.presence_of_element_located((By.XPATH, self._group_by_label_xpath(label) + "//textarea")))
        self._scroll_into_view(el)
        return el
    
    # def open_users_list(self):
    #     # Use if you aren’t already on Users list page
    #     self.wait.until(EC.url_contains("/web/index.php/claim/viewAssignClaim"))
    def open_users_list(self):
        """Navigate to Employee Claims list (keeps your existing test name)."""
        self.wait.until(EC.element_to_be_clickable(self.EMPLOYEE_CLAIMS_TAB)).click()
        self.wait.until(EC.visibility_of_element_located(self.TABLE_BODY))

    def _row_for_employee(self, full_name: str):
        return (
            By.XPATH,
            "//div[contains(@class,'oxd-table-body')]"
            "//div[contains(@class,'oxd-table-card')]"
            f"[.//*[contains(normalize-space(),\"{full_name}\")]]"
        )
    
    def search_user(self, full_name: str) -> bool:
        """
        Filters the Employee Claims list by Employee Name and returns True
        if at least one row for that employee exists.
        """
        # Focus Employee Name input
        inp = self.wait.until(EC.element_to_be_clickable(self.EMPLOYEE_NAME_INPUT))
        inp.click()
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        # Type a hint (two letters are enough for the demo; full name also fine)
        hint = full_name[:2] if len(full_name) >= 2 else full_name
        inp.send_keys(hint)

        # Pick exact suggestion
        listbox = self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, "(//div[@role='listbox'])[last()]")
        ))
        try:
            self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "(//div[@role='listbox'])[last()]//div[@role='option']"
                f"[.//span[normalize-space()=\"{full_name}\"]]"
            ))).click()
        except TimeoutException:
            return False  # no exact suggestion → no results

        # Search and wait for table refresh
        old_body = self.wait.until(EC.presence_of_element_located(self.TABLE_BODY))
        self.wait.until(EC.element_to_be_clickable(self.SEARCH_BTN)).click()
        try:
            self.wait.until(EC.staleness_of(old_body))
        except Exception:
            pass
        self.wait.until(EC.visibility_of_element_located(self.TABLE_BODY))

        # Rows for that employee?
        rows = self.driver.find_elements(*self._row_for_employee(full_name))
        return len(rows) > 0


    # def search_user(self, username) -> bool:
    #     # type username in filter
    #     box = self.wait.until(EC.element_to_be_clickable(self.USERNAME))
    #     box.click()
    #     box.send_keys(Keys.CONTROL, "a")
    #     box.send_keys(Keys.DELETE)
    #     box.send_keys(username)
    #  # click Search and wait for the table to refresh
    #     old_body = self.wait.until(EC.presence_of_element_located(self.TABLE_BODY))
    #     self.wait.until(EC.element_to_be_clickable(self.SEARCH_BTN)).click()
    #     self.wait.until(EC.staleness_of(old_body))
    #     self.wait.until(EC.visibility_of_element_located(self.TABLE_BODY))

    #     # return True iff there’s a row with that exact username
    #     rows = self.driver.find_elements(*self._row_for_user(username))
    #     return len(rows) > 0
    
    def _row_for_user(self, username: str):
        return (By.XPATH,f"//div[contains(@class,'oxd-table-card')][.//div[normalize-space()='{username}']]")

    def _clear_and_type(self, el: WebElement, text: str) -> None:
        self.wait.until(EC.visibility_of(el))
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(text)

   
    # ------------ Employee Name autocomplete ------------
    def select_employee_autocomplete(self, typed_text: str, option_text: Optional[str] = None, index: int = 1) -> WebElement:
        """
        Type into 'Employee Name' and select a suggestion.
        - If option_text is given, picks the first suggestion whose full text contains all tokens (case-insensitive).
        - Else selects by 1-based index.
        """
        inp = self._input_by_label("Employee Name")
        self._clear_and_type(inp, typed_text)

        listbox = self.wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[@role='listbox'])[last()]")))
        options: List[WebElement] = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "(//div[@role='listbox'])[last()]//div[@role='option']"))
        )

        if option_text:
            tokens = [t.lower() for t in option_text.split() if t.strip()]
            match = None
            available = []
            for opt in options:
                label = " ".join((opt.text or "").split()).lower()
                available.append(label)
                if all(tok in label for tok in tokens):
                    match = opt
                    break
            if not match:
                raise AssertionError(f"No autocomplete option matching '{option_text}'. Typed='{typed_text}'. Available={available}")
            match.click()
        else:
            if index < 1 or index > len(options):
                raise IndexError(f"index {index} out of range (1..{len(options)})")
            options[index - 1].click()

        # optional: wait it to close
        try:
            WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located((By.XPATH, "(//div[@role='listbox'])[last()]")))
        except TimeoutException:
            pass
        return inp
    
    def _select_dropdown_by_label(self, label: str, option_text: str) -> WebElement:
        group = self._group_by_label_xpath(label)
        wrapper = (By.XPATH, group + "//div[contains(@class,'oxd-select-text')]")
        display = (By.XPATH, group + "//div[contains(@class,'oxd-select-text-input')]")

        self.wait.until(EC.element_to_be_clickable(wrapper)).click()
        # pick from the floating dropdown (appended to body)
        opt = (By.XPATH, f"(//div[contains(@class,'oxd-select-dropdown')])[last()]//span[normalize-space()=\"{option_text}\"]")
        self.wait.until(EC.element_to_be_clickable(opt)).click()

        disp = self.wait.until(EC.visibility_of_element_located(display))
        # small, non-blocking confirmation
        try:
            WebDriverWait(self.driver, 2).until(lambda d: disp.text.strip() == option_text)
        except TimeoutException:
            pass
        return disp

    

    # ——— Navigation to Employee Claims list ———
    

    # ——— Helpers ———
    

    # ——— Search by Employee Name (autocomplete) ———
    