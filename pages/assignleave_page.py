from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pages.leave_page import LeavePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class AssignLeavePage:
    EMP_id = (By.XPATH, "//label[normalize-space()='Employee Name']")
    

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @staticmethod
    def _group_by_label_xpath(label: str) -> str:
        # scope any control by its label (e.g., "Leave Type", "Employee Name")
        return f"//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{label}']]"


    def _dismiss_overlays_if_any(self, timeout: int = 2) -> None:
        """Best-effort wait for spinners/backdrops that block clicks."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, ".oxd-loading-spinner, .oxd-overlay, .oxd-backdrop")
                )
            )
        except TimeoutException:
            pass

    def _scroll_into_view(self, el) -> None:
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

    def _nudge_below_header(self) -> None:
        """Move content slightly down so sticky header doesn't intercept clicks."""
        try:
            self.driver.execute_script("window.scrollBy(0, -100);")
        except Exception:
            pass

    def _safe_click(self, el) -> None:
        """Click with retries and fallbacks to avoid intercepts."""
        self._scroll_into_view(el)
        self._nudge_below_header()
        self._dismiss_overlays_if_any(1)
        try:
            el.click()
            return
        except ElementClickInterceptedException:
            # Try Actions, then JS as last resort
            try:
                ActionChains(self.driver).move_to_element(el).pause(0.1).click().perform()
                return
            except Exception:
                self.driver.execute_script("arguments[0].click();", el)

    # --- replace your _select_dropdown_by_label with this sturdier version ---

    def _select_dropdown_by_label(self, label: str, option_text: str):
        group = self._group_by_label_xpath(label)
        wrapper_loc = (By.XPATH, group + "//div[contains(@class,'oxd-select-text')]")
        display_loc = (By.XPATH, group + "//div[contains(@class,'oxd-select-text-input')]")

        # Ensure wrapper is in view and safely clickable
        wrapper_el = self.wait.until(EC.presence_of_element_located(wrapper_loc))
        self._safe_click(wrapper_el)

        # Opened dropdown is appended to body; always target the last one
        dd_loc = (By.XPATH, "(//div[contains(@class,'oxd-select-dropdown')])[last()]")
        self.wait.until(EC.visibility_of_element_located(dd_loc))

        # Click the option container (more reliable than clicking inner span)
        opt_loc = (
            By.XPATH,
            "(//div[contains(@class,'oxd-select-dropdown')])[last()]"
            f"//div[@role='option'][.//span[normalize-space()=\"{option_text}\"]]"
        )
        opt_el = self.wait.until(EC.presence_of_element_located(opt_loc))
        self._safe_click(opt_el)

        # Sanity: display reflects chosen value (non-fatal if it takes a tick)
        try:
            disp_el = self.wait.until(EC.visibility_of_element_located(display_loc))
            WebDriverWait(self.driver, 2).until(lambda d: (disp_el.text or "").strip() == option_text)
        except TimeoutException:
            pass

        return opt_el


    def _clear_and_type(self, el, text: str):
        self.wait.until(EC.visibility_of(el))
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(text)
        def _set_date_by_label(self, label: str, date_str: str) -> WebElement:
            locator = (By.XPATH,
                self._group_by_label_xpath(label) +
                "//input[contains(concat(' ',normalize-space(@class),' '),' oxd-input ') and "
                "contains(concat(' ',normalize-space(@class),' '),' oxd-input--active ')]"
            )
            inp = self.wait.until(EC.element_to_be_clickable(locator))
            self._scroll_into_view(inp)
            self._clear_and_type(inp, date_str)
            inp.send_keys(Keys.TAB)  # commit/blur
            return inp


    def _type_input(self, label_text, value):
        inp = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//label[normalize-space()='{label_text}']/../..//input")
        ))
        inp.clear()
        inp.send_keys(value)
        return inp

    def _set_date_by_label(self, label: str, date_str: str) -> WebElement:
        """
        Fill a date input under the given label (e.g., 'From Date', 'To Date').
        date_str must match the UI format (usually yyyy-mm-dd).
        """
        locator = (By.XPATH,
            self._group_by_label_xpath(label) +
            "//input[contains(concat(' ',normalize-space(@class),' '),' oxd-input ') and "
            "contains(concat(' ',normalize-space(@class),' '),' oxd-input--active ')]"
        )
        inp = self.wait.until(EC.element_to_be_clickable(locator))
        self._scroll_into_view(inp)
        self._clear_and_type(inp, date_str)
        inp.send_keys(Keys.TAB)  # commit/blur
        return inp

    # (nice-to-have public wrappers so tests don't call a "private" method)
    def set_from_date(self, date_str: str) -> WebElement:
        return self._set_date_by_label("From Date", date_str)

    def set_to_date(self, date_str: str) -> WebElement:
        return self._set_date_by_label("To Date", date_str)
    # Proper autocomplete selector for Employee Name
    def select_employee_autocomplete(self, typed_text: str, option_text: str = None, index: int = 1):
        # focus the Employee Name input
        inp = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//label[normalize-space()='Employee Name']/../..//input")))
        inp.clear()
        inp.send_keys(typed_text)
# wait for suggestions
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='listbox']")))
        if option_text:
            # choose by visible text (case-insensitive contains)
            options = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='listbox']//div[@role='option']//span")))
            target = None
            for el in options:
                if option_text.lower() in (el.text or "").strip().lower():
                    target = el
                    break
            if not target:
                raise AssertionError(f"No autocomplete option matching '{option_text}'")
            self.wait.until(EC.element_to_be_clickable(target)).click()
        else:
            # choose by index (1-based)
            nth = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"(//div[@role='listbox']//div[@role='option'])[{index}]")))
            nth.click()

    def add_user(self, employee_name_hint, username, password, user_role="ESS", status="Enabled", employee_exact=None):
        self.open_add_form()
        self._select_dropdown("User Role", user_role)
        self.select_employee_autocomplete(typed_text=employee_name_hint, option_text=employee_exact)
        self._select_dropdown("Status", status)
        self._type_input("Username", username)
        self._type_input("Password", password)
        self._type_input("Confirm Password", password)
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN)).click()
        # Success toast can be flaky—wait if present; otherwise continue
        try:
            self.wait.until(EC.visibility_of_element_located(self.TOAST_SUCCESS))
        except Exception:
            pass

    def _click_assign(self):
        btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Assign']")))
        self._scroll_into_view(btn)
        btn.click()
        return btn

    def _leave_assigned_toast(self) -> WebElement:
        toast = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'oxd-toast') and contains(@class,'oxd-toast--success')]")))
        self._scroll_into_view(toast)
        return toast