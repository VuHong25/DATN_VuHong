
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class SearchPage(BasePage):
    """
    Page Object đại diện cho khu vực tìm kiếm của TrueMart.
    Kế thừa BasePage để dùng lại: find(), safe_click(), check_visible()…
    """
    INPUT_SEARCH = (By.NAME, "searchString")

    BTN_SEARCH = (By.CLASS_NAME, "submit-btn")

    PRODUCT_CARDS = (By.CSS_SELECTOR, ".single-product")

    MSG_NOT_FOUND = (By.XPATH,
        "//div[@id='grid-view']//h4[contains(.,'Không tìm thấy sản phẩm nào')]"
    )

    PRODUCT_NAME = (By.CSS_SELECTOR,
        ".single-product .product-name, "
        ".single-product h3, "
        ".single-product h4, "
        ".single-product h5, "
        ".single-product .title, "
        ".single-product [class*='name'], "
        ".single-product [class*='title'], "
        ".single-product a.product-title, "
        ".single-product p.name"
    )

    # ------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------

    def open_home(self, base_url: str) -> None:
        """Mở trang chủ. driver.get() điều hướng trình duyệt đến URL."""
        self.open(base_url)

    # ------------------------------------------------------------------
    # ACTIONS – mô phỏng hành vi người dùng
    # ------------------------------------------------------------------

    def search(self, keyword: str) -> None:
        """
        Gõ từ khóa vào ô tìm kiếm và click nút kính lúp.
        """
        el = WebDriverWait(self.driver, 7).until(
            EC.element_to_be_clickable(self.INPUT_SEARCH)
        )
        el.clear()                        # xóa text cũ tránh nối chuỗi
        el.send_keys(keyword)
        self.safe_click(self.BTN_SEARCH)  # scroll + wait clickable + click
        self._wait_result()

    def search_by_enter(self, keyword: str) -> None:
        """
        Gõ từ khóa và nhấn phím Enter thay vì click button.
        """
        el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.INPUT_SEARCH)
        )
        el.clear()
        el.send_keys(keyword)
        el.send_keys(Keys.RETURN)
        self._wait_result()

    def _wait_result(self) -> None:
        """
        Chờ trang kết quả load xong.
        Điều kiện dừng: có ít nhất 1 card sản phẩm HOẶC thông báo not-found.
        """
        try:
            WebDriverWait(self.driver, 7).until(
                lambda d:
                    len(d.find_elements(*self.PRODUCT_CARDS)) > 0
                    or len(d.find_elements(*self.MSG_NOT_FOUND)) > 0
            )
        except TimeoutException:
            pass  # để test tự assert, tránh ẩn lỗi

    # ------------------------------------------------------------------
    # GETTERS – lấy thông tin từ trang kết quả để dùng trong assert
    # ------------------------------------------------------------------

    def get_product_count(self) -> int:
        """
        Đếm số card sản phẩm đang hiển thị.
        """
        return len(self.driver.find_elements(*self.PRODUCT_CARDS))

    def is_not_found_visible(self) -> bool:
        """
        Kiểm tra thông báo 'Không tìm thấy' có đang hiển thị không.

        """
        return self.check_visible(self.MSG_NOT_FOUND)

    def get_not_found_text(self) -> str:
        """
        Lấy nội dung text thông báo không tìm thấy.
        Trả về "" nếu thông báo không xuất hiện trong 5s.
        """
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.MSG_NOT_FOUND)
            )
            return el.text.strip()
        except TimeoutException:
            return ""

    def get_product_names(self) -> list[str]:
        self._wait_for_cards()

        try:
            elements = self.driver.find_elements(*self.PRODUCT_NAME)
            names = [el.text.strip().lower() for el in elements if el.text.strip()]
            if names:
                return names
        except Exception:
            pass

        try:
            cards = self.driver.find_elements(*self.PRODUCT_CARDS)
            names = []
            for card in cards:
                text = card.text.strip()
                if text:
                    # Lấy dòng đầu tiên không rỗng làm tên sản phẩm
                    first_line = next(
                        (line.strip().lower() for line in text.splitlines()
                         if line.strip()),
                        ""
                    )
                    if first_line:
                        names.append(first_line)
            return names
        except Exception:
            return []

    def _wait_for_cards(self) -> None:
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(self.PRODUCT_CARDS)
            )
        except TimeoutException:
            pass

    # -----------------------------------------------------------------


