from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains

class LoginPage(BasePage):
    menu_account = (By.XPATH, "//a[contains(text(),'Tài khoản')]")
    link_login = (By.XPATH, "//a[contains(text(),'Đăng nhập')]")
    # link_register = (By.XPATH, "//a[contains(text(),'Đăng ký')]")

    input_username = (By.NAME, "username")
    input_password = (By.NAME, "password")
    btn_login = (By.CLASS_NAME, "return-customer-btn")
    msg_error = (By.XPATH, "//span[@data-valmsg-for='ErrorLogin']")

# điền form
    def _open_account_dropdown(self):
        # Tìm menu Tài khoản
        menu = self.find(self.menu_account)
        # Thực hiện hành động Hover (di chuột)
        actions = ActionChains(self.driver)
        actions.move_to_element(menu).perform()

    def open_login_page(self, base_url):
        self.open(base_url)
        self._open_account_dropdown()
        self.safe_click(self.link_login)

    def login(self, username, password):
        self.type_text(self.input_username, username)
        self.type_text(self.input_password, password)
        self.safe_click(self.btn_login)
    # ----------------------------------------------------------    # ----------------------------------------------------------
    def get_error_message(self):
        return self.get_text(self.msg_error)

    # ----------------------------------------------------------
    # Kiểm tra xem thông báo lỗi có hiện ra không
    # ----------------------------------------------------------
    def check_error_visible(self):
        return self.check_visible(self.msg_error)
    
    def get_span_error_text(self, timeout=5):
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.msg_error)
            )
            return el.text.strip()
        except:
            return ""   # luôn trả về string