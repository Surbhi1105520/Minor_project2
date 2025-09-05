from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pages.leave_page import LeavePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class AssignClaimPage:
    CREATE_BTN = (By.XPATH, "//button[@type='submit']")
    TOAST_CLOSE = (By.XPATH,"//div[contains(@class,'oxd-toast')]//button[contains(@class,'oxd-toast-close')]")
    SUCCESS_TOAST = (
        By.XPATH,
        "//div[contains(@class,'oxd-toast') and contains(@class,'oxd-toast--success')]"
    )
    TOAST_CLOSE = (
        By.XPATH,
        # close button can be a <button> or an element with close class; handle both
        "//div[contains(@class,'oxd-toast')]//button[contains(@class,'oxd-toast-close')]"
        " | //div[contains(@class,'oxd-toast')]//*[contains(@class,'oxd-toast-close')]"
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @staticmethod
    def _group_by_label_xpath(label: str) -> str:
        # scope any control by its label (e.g., "Leave Type", "Employee Name")
        return f"//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{label}']]"
    
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

    def wait_success_toast(self, timeout: int = 8):
        """Wait for and return the success toast element."""
        toast = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.SUCCESS_TOAST)
        )
        # optional: scroll into view
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", toast)
        return toast

    def is_success_toast_visible(self, timeout: int = 8) -> bool:
        try:
            self.wait_success_toast(timeout)
            return True
        except TimeoutException:
            return False

    def close_success_toast(self) -> None:
        """Click the toast close button, or wait for auto-dismiss."""
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


    def select_event(self, event_text: str):
        """Selects an Event (e.g., 'Accommodation', 'Travel', 'Conference')."""
        return self._select_dropdown_by_label("Event", event_text)

    def select_currency(self, currency_text: str):
        """Selects a Currency (e.g., 'USD - United States Dollar', 'INR - Indian Rupee')."""
        return self._select_dropdown_by_label("Currency", currency_text)

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

    
    def is_success_toast_visible(self, timeout: int = 8) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.SUCCESS_TOAST)
            )
            return True
        except TimeoutException:
            return False



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
    
    


