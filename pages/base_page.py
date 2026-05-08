from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # tìm phần  tử
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def safe_click_1(self, locator):
        # Chờ phần tử xuất hiện trong DOM
        element = self.wait.until(EC.presence_of_element_located(locator))
        # Cuộn tới phần tử để tránh bị menu hoặc banner che khuất
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        # Chờ cho đến khi có thể click được (hết hiệu ứng load)
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text

    #kiểm tra xem một phần từ có đang hiển thị trên màn hình hay không
    def check_visible(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    # mở một đường dẫn URL bất kỳ
    def open(self, url):
        self.driver.get(url)

    def safe_click(self, locator):
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(locator)
        )

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)

    def is_field_invalid_html5(self, locator) -> bool:
        """
        Kiểm tra trường có bị HTML5 đánh dấu invalid không.
        Dùng checkValidity() trả về False nếu trường không hợp lệ.
        """
        el = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].focus();", el)
        return not self.driver.execute_script(
            "return arguments[0].checkValidity();", el
        )