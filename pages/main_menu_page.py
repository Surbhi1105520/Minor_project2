from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from pages.login_page import LoginPage

class MainMenu:
    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index"

    # Locators
    DASH_H6  = (By.CSS_SELECTOR, "h6.oxd-text.oxd-text--h6.oxd-topbar-header-breadcrumb-module")
    WELCOME_BANNER = (By.CSS_SELECTOR, "div.oxd-layout-context div.orangehrm-dashboard")
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def _menu_link(self, text: str):
        # <a> that wraps the <span> with the visible menu text
        return (By.XPATH, f"//aside//a[.//span[normalize-space()='{text}']]")

    # def is_visible(self, text: str) -> bool:
    #     el = self.wait.until(EC.visibility_of_element_located(self._menu_link(text)))
    #     return el.is_displayed() and el.is_enabled()


    def is_visible(self, text, timeout=2):
        """Return True if menu item is visible within timeout; False otherwise."""
        locator = self._menu_link(text)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    def click(self, text):
        el = self.wait.until(EC.element_to_be_clickable(self._menu_link(text)))
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def wait_landed(self, path_fragment):
        self.wait.until(EC.url_contains(path_fragment))


    def is_welcome_banner_visible(self) -> bool:
        try:
            banner = self.wait.until(EC.visibility_of_element_located(self.WELCOME_BANNER))
            return banner.is_displayed()
        except Exception:
            return False
        
    