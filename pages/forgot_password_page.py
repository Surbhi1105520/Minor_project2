from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ForgotPasswordPage:
    # Login page link (the <p> “Forgot your password?” is clickable)
    FORGOT_LINK = (By.CSS_SELECTOR, "p.orangehrm-login-forgot-header")
    # Forgot Password page
    USERNAME_INPUT = (By.XPATH, "//label[normalize-space()='Username']/../..//input")
    RESET_BTN      = (By.XPATH, "//button[normalize-space()='Reset Password']")
    # Success signals (the demo often shows a success toast; sometimes a panel)
    SUCCESS_TOAST  = (By.XPATH, "//div[contains(@class,'oxd-toast') and .//p[contains(.,'Success')]]")
    SUCCESS_PANEL  = (By.XPATH, "//p[contains(.,'Reset Password') or contains(.,'password reset') or contains(.,'email')]")

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def open_from_login(self):
        """Click 'Forgot your password?' on the login page."""
        self.wait.until(EC.element_to_be_clickable(self.FORGOT_LINK)).click()
        self.wait.until(EC.url_contains("/requestPasswordResetCode"))

    def request_reset(self, username: str):
        """Enter username and submit reset."""
        box = self.wait.until(EC.element_to_be_clickable(self.USERNAME_INPUT))
        box.clear()
        box.send_keys(username)
        self.wait.until(EC.element_to_be_clickable(self.RESET_BTN)).click()

    def wait_for_confirmation(self):
        """
        Wait for any confirmation the request was accepted:
        - preferred: success toast
        - fallback: confirmation panel/text on the page
        Returns the element that confirmed success (toast or panel).
        """
        try:
            return self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        except Exception:
            return self.wait.until(EC.visibility_of_element_located(self.SUCCESS_PANEL))
