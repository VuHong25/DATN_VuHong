

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from pages.base_page import BasePage
from pages.search_page import SearchPage


class ProductDetailPage(BasePage):
    """Page Object cho trang Xem Chi Tiết Sản Phẩm."""

    # ----------------------------------------------------------
    # LOCATORS – THÔNG TIN SẢN PHẨM
    # ----------------------------------------------------------
    PRODUCT_NAME      = (By.CLASS_NAME, "product-header")
    PRODUCT_PRICE     = (By.CLASS_NAME, "new-price")
    PRODUCT_PRICE_OLD = (By.CLASS_NAME, "old-price")
    PRODUCT_IMAGE     = (By.ID, "modal-hinhanh")

    # ----------------------------------------------------------
    # LOCATORS – TƯƠNG TÁC
    # ----------------------------------------------------------
    DROPDOWN_SIZE   = (By.ID, "product-size")
    BTN_ADD_TO_CART = (By.ID, "order-text")
    INPUT_QUANTITY  = (By.ID, "modal-soluong")

    # ----------------------------------------------------------
    # LOCATORS – SWEETALERT 
    # ----------------------------------------------------------
    SWAL_TITLE  = (By.XPATH,
        "//div[contains(@class,'swal-title') or contains(@class,'swal2-title')]"
    )
    SWAL_TEXT   = (By.XPATH,
        "//div[contains(@class,'swal-text')"
        " or contains(@class,'swal2-html-container')]"
    )
    BTN_SWAL_OK = (By.XPATH,
        "//button[contains(@class,'swal-button--confirm')"
        " or contains(@class,'swal2-confirm')]"
    )

    # ----------------------------------------------------------
    # LOCATORS – ĐÁNH GIÁ
    # ----------------------------------------------------------
    REVIEW_SECTION = (By.XPATH,
        "//*[@id='box-danhgia'"
        " or @id='danh-sach-danhgia'"
        " or @id='danh-sach-danh-gia']"
    )
    MSG_NO_REVIEW = (By.XPATH,
        "//*[contains(normalize-space(.),'Chưa có đánh giá nào')]"
    )

    # ==========================================================
    # STATIC – XPath link SP hợp lệ
    # ==========================================================

    @staticmethod
    def _product_link_xpath(index: int = 1) -> str:
        digits = " or ".join(
            f"substring(@href,string-length(@href),1)='{d}'"
            for d in "0123456789"
        )
        return (
            f"(//a[contains(@href,'Product/ProductDetail')"
            f" and ({digits})])[{index}]"
        )

    # ==========================================================
    # NAVIGATION
    # ==========================================================

    def navigate_by_search(self, base_url: str, keyword: str):
    
        search_page = SearchPage(self.driver)
        search_page.open_home(base_url)
        search_page.search(keyword)

        locator = (By.XPATH, self._product_link_xpath(1))
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
            el = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)
            self._wait_for_product_detail_page()
        except TimeoutException:
            fallback = (By.XPATH,
                "//div[contains(@class,'single-product')]"
                "//a[contains(@href,'ProductDetail')]"
            )
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(fallback)
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                self.driver.execute_script("arguments[0].click();", el)
                self._wait_for_product_detail_page()
            except TimeoutException:
                pass

    def navigate_by_click_on_homepage(self, base_url: str, product_index: int = 1):
        self.open(base_url)
        locator = (By.XPATH, self._product_link_xpath(product_index))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
        el = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)
        self._wait_for_product_detail_page()

    # ==========================================================
    # WAIT HELPERS
    # ==========================================================

    def _wait_for_product_detail_page(self, timeout: int = 10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: "productdetail" in d.current_url.lower()
        )

    def wait_for_swal_appear(self, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.SWAL_TITLE)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_swal_disappear(self, timeout: int = 8) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.SWAL_TITLE)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_btn_text_update(self, timeout: int = 5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.is_add_to_cart_btn_disabled()
                          or self.is_swal_visible()
            )
        except TimeoutException:
            pass

    # ==========================================================
    # GETTERS
    # ==========================================================

    def get_product_name(self) -> str:
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.PRODUCT_NAME)
            ).text.strip()
        except TimeoutException:
            return ""

    def get_product_price(self) -> str:
        for loc in (self.PRODUCT_PRICE, self.PRODUCT_PRICE_OLD):
            try:
                text = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(loc)
                ).text.strip()
                if text:
                    return text
            except TimeoutException:
                continue
        return ""

    def get_add_to_cart_btn_text(self) -> str:
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.BTN_ADD_TO_CART)
            ).text.strip()
        except TimeoutException:
            return ""

    def get_swal_title(self) -> str:
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.SWAL_TITLE)
            ).text.strip()
        except TimeoutException:
            return ""

    def get_swal_text(self) -> str:
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.SWAL_TEXT)
            ).text.strip()
        except TimeoutException:
            return ""

    def get_size_options(self) -> list:
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.DROPDOWN_SIZE)
            )
            return [opt.text.strip() for opt in Select(el).options]
        except (TimeoutException, NoSuchElementException):
            return []

    def get_review_section_text(self) -> str:
        xpaths = [
            "//*[@id='box-danhgia']",
            "//*[@id='danh-sach-danhgia']",
            "//*[@id='danh-sach-danh-gia']",
        ]
        for xpath in xpaths:
            try:
                el = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                text = el.text.strip()
                if text:
                    return text
            except TimeoutException:
                continue
        return ""

    def get_current_url(self) -> str:
        return self.driver.current_url

    # ==========================================================
    # CHECKERS
    # ==========================================================

    def is_on_product_detail_page(self) -> bool:
        return "productdetail" in self.driver.current_url.lower()

    def is_product_name_visible(self) -> bool:
        return self.check_visible(self.PRODUCT_NAME)

    def is_product_price_visible(self) -> bool:
        return (
            self.check_visible(self.PRODUCT_PRICE)
            or self.check_visible(self.PRODUCT_PRICE_OLD)
        )

    def is_product_image_displayed(self) -> bool:
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.PRODUCT_IMAGE)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_add_to_cart_btn_visible(self) -> bool:
        return self.check_visible(self.BTN_ADD_TO_CART)

    def is_add_to_cart_btn_enabled(self) -> bool:
        try:
            el = self.driver.find_element(*self.BTN_ADD_TO_CART)
            return el.is_enabled() and el.get_attribute("disabled") is None
        except Exception:
            return False

    def is_add_to_cart_btn_disabled(self) -> bool:
        try:
            el = self.driver.find_element(*self.BTN_ADD_TO_CART)
            return (not el.is_enabled()) or (el.get_attribute("disabled") is not None)
        except Exception:
            return False

    def is_size_dropdown_visible(self) -> bool:
        return self.check_visible(self.DROPDOWN_SIZE)

    def is_swal_visible(self) -> bool:
        return self.check_visible(self.SWAL_TITLE)

    def is_no_review_message_visible(self) -> bool:
        if self.check_visible(self.MSG_NO_REVIEW):
            return True
        return "Chưa có đánh giá nào" in self.get_review_section_text()

    # ==========================================================
    # ACTIONS
    # ==========================================================

    def select_size(self, size_text: str = None, size_index: int = 1):
        
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.DROPDOWN_SIZE)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            sel = Select(el)
            if size_text:
                sel.select_by_visible_text(size_text)
            else:
                sel.select_by_index(size_index)
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", el
            )
        except (TimeoutException, NoSuchElementException):
            pass

    def set_quantity(self, value: int):
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.INPUT_QUANTITY)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].value = '';", el)
            el.send_keys(str(value))
        except (TimeoutException, NoSuchElementException):
            pass

    def click_add_to_cart(self):
        el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_ADD_TO_CART)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def click_add_to_cart_and_wait_swal(self, timeout: int = 5) -> bool:
        self.click_add_to_cart()
        return self.wait_for_swal_appear(timeout=timeout)

    def close_swal_if_visible(self):
        if not self.is_swal_visible():
            return
        try:
            WebDriverWait(self.driver, 4).until(lambda d: not self.is_swal_visible())
        except TimeoutException:
            try:
                btn = self.driver.find_element(*self.BTN_SWAL_OK)
                self.driver.execute_script("arguments[0].click();", btn)
            except NoSuchElementException:
                pass

    def scroll_to_review_section(self):
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.REVIEW_SECTION)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except TimeoutException:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")



