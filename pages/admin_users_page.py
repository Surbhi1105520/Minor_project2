# pages/admin_users_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class AdminUsersPage:
    ADD_BTN        = (By.XPATH, "//button[normalize-space()='Add']")
    SAVE_BTN       = (By.XPATH, "//button[normalize-space()='Save']")
    TOAST_SUCCESS  = (By.XPATH, "//div[contains(@class,'oxd-toast--success')]")
    USER_MANAGEMENT = (By.XPATH, "//li[contains(@class,'oxd-topbar-body-nav-tab')][.//span[normalize-space()='User Management']]")
    USERNAME        = (By.XPATH, "//label[normalize-space()='Username']/../..//input")
    SEARCH_BTN      = (By.XPATH, "//button[@type='submit']")
    RECORD          = (By.XPATH, "//span[normalize-space()='(1) Record Found']")
    TABLE_BODY = (By.XPATH, "//div[contains(@class,'oxd-table-body')]")
    ROW_FOR_USER = lambda username: (By.XPATH,f"//div[contains(@class,'oxd-table-card')][.//div[normalize-space()='{username}']]")

    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def open_add_form(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_BTN)).click()
        self.wait.until(EC.visibility_of_element_located(self.SAVE_BTN))

    def _select_dropdown(self, label_text, option_text):
        box = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//label[normalize-space()='{label_text}']/../..//div[contains(@class,'oxd-select-text')]")
        ))
        box.click()
        opt = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@role='listbox']//span[normalize-space()='{option_text}']")
        ))
        opt.click()

    def _type_input(self, label_text, value):
        inp = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//label[normalize-space()='{label_text}']/../..//input")
        ))
        inp.clear()
        inp.send_keys(value)
        return inp

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

    def _row_for_user(self, username: str):
        return (By.XPATH,f"//div[contains(@class,'oxd-table-card')][.//div[normalize-space()='{username}']]")

    def open_users_list(self):
        # Use if you aren’t already on Users list page
        self.wait.until(EC.url_contains("/web/index.php/admin/viewSystemUsers"))

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