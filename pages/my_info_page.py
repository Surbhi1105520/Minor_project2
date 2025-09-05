from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class MyInfoPage:
    TABS_CONTAINER = (By.XPATH, "//div[contains(@class,'orangehrm-tabs') or contains(@class,'orangehrm-edit-employee')]")

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    # def _tab_link(self, text: str):
    #     alt = text.replace("-", " ")
    #     return (
    #         By.XPATH,
    #         (
    #             "//div[contains(@class,'orangehrm-tabs') or contains(@class,'orangehrm-edit-employee')]"
    #             "//a[normalize-space()='{t}' or .//span[normalize-space()='{t}'] "
    #             " or normalize-space()='{alt}' or .//span[normalize-space()='{alt}']]"
    #         ).format(t=text, alt=alt)
    #     )

    def _tab_active(self, text: str):
        alt = text.replace("-", " ")
        return (
            By.XPATH,
            (
                "//a[contains(@class,'--active')][normalize-space()='{t}' or .//span[normalize-space()='{t}'] "
                " or normalize-space()='{alt}' or .//span[normalize-space()='{alt}']]"
            ).format(t=text, alt=alt)
        )

    def _header_h6(self, text: str):
        alt = text.replace("-", " ")
        return (
            By.XPATH,
            "//h6[contains(@class,'orangehrm-main-title')][normalize-space()='{t}' or normalize-space()='{alt}']"
            .format(t=text, alt=alt)
        )

    def ensure_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.TABS_CONTAINER))

    def _tab_link(self, text: str):
        alt = text.replace("-", " ")
        return (
            By.XPATH,
            (
                "//div[contains(@class,'orangehrm-tabs') or contains(@class,'orangehrm-edit-employee')]"
                "//a[normalize-space()='{t}' or .//span[normalize-space()='{t}'] "
                " or normalize-space()='{alt}' or .//span[normalize-space()='{alt}']]"
            ).format(t=text, alt=alt)
        )

    def is_tab_visible(self, text: str, timeout: int = 3) -> bool:
        """Return True if tab is visible within timeout; False otherwise."""
        locator = self._tab_link(text)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # def is_tab_visible(self, text: str) -> bool:
    #     self.ensure_loaded()
    #     el = self.wait.until(EC.visibility_of_element_located(self._tab_link(text)))
    #     return el.is_displayed() and el.is_enabled()

    def click_tab(self, text: str):
        self.ensure_loaded()
        el = self.wait.until(EC.element_to_be_clickable(self._tab_link(text)))
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def wait_landed(self, text: str, path_fragment: str = None):
        """
        Robust landing check:
        1) Try URL (short), then
        2) Active tab OR header h6 matching the tab text.
        """
        if path_fragment:
            from selenium.webdriver.support.wait import WebDriverWait
            try:
                WebDriverWait(self.driver, 3).until(EC.url_contains(path_fragment))
                return
            except Exception:
                pass  # fall through to UI-based checks

        # Active tab
        try:
            self.wait.until(EC.visibility_of_element_located(self._tab_active(text)))
            return
        except Exception:
            # Header h6 fallback
            self.wait.until(EC.visibility_of_element_located(self._header_h6(text)))
