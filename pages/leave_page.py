from dataclasses import dataclass
from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class LeavePage:
    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def open_assign_leave(self) -> None:
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='oxd-topbar-body-nav-tab-item' and normalize-space()='Assign Leave']")
        )).click()
        self.wait.until(EC.url_contains("/web/index.php/leave/assignLeave"))

    @staticmethod
    def _group_by_label_xpath(label: str) -> str:
        # wrapper for any field group that contains this label
        return f"//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{label}']]"

    # --- quick check that the Assign Leave page is loaded ---
    def assign_leave_landed(self) -> bool:
        try:
            # page title
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//h6[normalize-space()='Assign Leave']")))
            # and the Employee Name group exists
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, self._group_by_label_xpath('Employee Name'))))
            return True
        except TimeoutException:
            return False

    def open_leave_list(self) -> None:
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href,'/web/index.php/leave/viewLeaveList') or .//span[normalize-space()='Leave List']]")
        )).click()
        self.wait.until(EC.url_contains("/web/index.php/leave/viewLeaveList"))

    # ------------ basic field helpers ------------
    def _input_by_label(self, label: str) -> WebElement:
        el = self.wait.until(EC.presence_of_element_located((By.XPATH, self._group_by_label_xpath(label) + "//input")))
        self._scroll_into_view(el)
        return el

    def _textarea_by_label(self, label: str) -> WebElement:
        el = self.wait.until(EC.presence_of_element_located((By.XPATH, self._group_by_label_xpath(label) + "//textarea")))
        self._scroll_into_view(el)
        return el

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



    # ------------ main action: Assign Leave ------------
    def assign_leave(
        self,
        employee_hint: str,
        employee_exact: str,
        leave_type: str,
        from_date: str,
        to_date: str,
        duration: str = "Full Day",
        comment: str = "",
    ) -> WebElement:
        # Employee
        self.select_employee_autocomplete(typed_text=employee_hint, option_text=employee_exact)

        # Leave Type (label is 'Leave Type'; option is the value you pass in)
        self._select_dropdown_by_label("Leave Type", leave_type)

        # Dates
        self._set_date_by_label("From Date", from_date)
        self._set_date_by_label("To Date", to_date)

        # Duration
        self._select_dropdown_by_label("Duration", duration)

        # Comment
        if comment:
            self._clear_and_type(self._textarea_by_label("Comment"), comment)

        # Assign + confirm
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Assign']"))).click()
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='document']//button[normalize-space()='Assign']"))).click()
        except TimeoutException:
            pass

        # Toast
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".oxd-toast, .oxd-toast-content")))

    # ------------ Leave List ------------
    def open_leave_list_if_needed(self) -> None:
        if "/web/index.php/leave/viewLeaveList" not in self.driver.current_url:
            self.open_leave_list()

    def filter_leave_list(self, employee_hint: str, employee_exact: str, from_date: str, to_date: str) -> None:
        self.open_leave_list_if_needed()
        body = (By.CSS_SELECTOR, ".oxd-table-body")
        old = self.wait.until(EC.presence_of_element_located(body))

        self.select_employee_autocomplete(employee_hint, option_text=employee_exact)
        self._set_date_by_label("From Date", from_date)
        self._set_date_by_label("To Date", to_date)

        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Search']"))).click()
        try:
            self.wait.until(EC.staleness_of(old))
        except TimeoutException:
            pass
        self.wait.until(EC.visibility_of_element_located(body))

    def has_result_row_for_date(self, from_date: str, to_date: Optional[str] = None) -> bool:
        if to_date:
            xpath = ("//div[contains(@class,'oxd-table-body')]//div[contains(@class,'oxd-table-card')]"
                     f"[.//*[contains(normalize-space(), '{from_date}')] and .//*[contains(normalize-space(), '{to_date}')]]")
        else:
            xpath = ("//div[contains(@class,'oxd-table-body')]//div[contains(@class,'oxd-table-card')]"
                     f"[.//*[contains(normalize-space(), '{from_date}')]]")
        return len(self.driver.find_elements(By.XPATH, xpath)) > 0
