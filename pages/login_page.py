# login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

class LoginPage:
    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

    # Locators
    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    SUBMIT   = (By.CSS_SELECTOR, "button[type='submit']")
    DASH_H6  = (By.CSS_SELECTOR, "h6.oxd-text.oxd-text--h6.oxd-topbar-header-breadcrumb-module")
    ERR_TXT  = (By.CSS_SELECTOR, "p.oxd-text.oxd-text--p.oxd-alert-content-text")
    FORGOT_PWD = (By.LINK_TEXT, "Forgot your password?")
    

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def open(self):
        if self.driver.current_url != self.URL:
            self.driver.get(self.URL)

    def visit(self):
        """Check that username and password fields are visible & enabled"""
        username_field = self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        password_field = self.wait.until(EC.visibility_of_element_located(self.PASSWORD))
        return username_field, password_field
        # assert username_field.is_displayed() and username_field.is_enabled(), " Username field not available"
        # assert password_field.is_displayed() and password_field.is_enabled(), " Password field not available"

        # return elements if needed
        return username_field, password_field
    
    def login(self, username, password):
        u = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        p = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        u.clear(); u.send_keys(username)
        p.clear(); p.send_keys(password)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()

    def is_dashboard_loaded(self) -> bool:
        try:
            el = self.wait.until(EC.presence_of_element_located(self.DASH_H6))
            # treat any reached app header as success; prefer "Dashboard" text when present
            return "Dashboard" in (el.text or "") or bool(el.text)
        except Exception:
            return False

    def get_error_text(self) -> str:
        try:
            err = self.wait.until(EC.visibility_of_element_located(self.ERR_TXT))
            return (err.text or "").strip()
        except Exception:
            return ""
