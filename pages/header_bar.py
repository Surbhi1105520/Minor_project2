from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class HeaderBar:
    USER_DROPDOWN = (By.XPATH, "//span[contains(@class,'oxd-userdropdown-tab')]")
    LOGOUT = (By.XPATH, "//a[normalize-space()='Logout']")

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def logout(self):
        self.wait.until(EC.element_to_be_clickable(self.USER_DROPDOWN)).click()
        self.wait.until(EC.element_to_be_clickable(self.LOGOUT)).click()
