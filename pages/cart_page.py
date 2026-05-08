
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from pages.base_page import BasePage


class CartPage(BasePage):

    # ==========================================================
    # LOCATORS  
    # ==========================================================

    ICON_CART = (By.XPATH, "//a[contains(@href,'/Cart/Orders')]")

    ROWS_CART_ITEM = (By.XPATH, "//tr[contains(@class,'cart_item')]")
    ITEM_NAME      = (By.CLASS_NAME, "product-name")
    TOTAL_PRICE    = (By.CLASS_NAME, "order-total")

    INPUTS_QUANTITY = (
        By.XPATH,
        "//tr[contains(@class,'cart_item')]"
        "//td[contains(@class,'product-quantity')]"
        "//input[@type='number']"
    )

    BTNS_INCREASE = (
        By.XPATH,
        "//tr[contains(@class,'cart_item')]//td[contains(@class,'product-quantity')]//input[@class='plus']"
    )

    BTNS_DECREASE = (
        By.XPATH,
        "//tr[contains(@class,'cart_item')]//td[contains(@class,'product-quantity')]//input[@class='minus']"
    )

    BTNS_REMOVE = (By.XPATH, "//td[@class='product-remove']/a")

    BTN_UPDATE_CART = (
        By.XPATH,
        "//div[contains(@class,'buttons-cart')]"
        "//a[contains(normalize-space(.),'Cập nhật giỏ hàng')]"
    )
    BTN_CONTINUE_SHOPPING = (
        By.XPATH,
        "//div[contains(@class,'buttons-cart')]"
        "//a[contains(normalize-space(.),'Tiếp tục mua sắm')]"
    )
    BTN_ORDER = (By.XPATH, "//div[contains(@class,'wc-proceed-to-checkout')]//a")

    POPUP_SWAL       = (By.XPATH, "//div[contains(@class,'swal-modal')]")
    MSG_SWAL_TITLE   = (By.XPATH, "//div[contains(@class,'swal-title')]")
    MSG_SWAL_TEXT    = (By.XPATH, "//div[contains(@class,'swal-text')]")
    BTN_CLOSE_SWAL   = (By.XPATH, "//div[contains(@class,'swal-footer')]//button")
    BTN_POPUP_OK     = (
        By.XPATH,
        "//button[contains(@class,'swal-button--confirm') and contains(normalize-space(.),'OK')]"
    )
    BTN_POPUP_CANCEL = (
        By.XPATH,
        "//button[contains(@class,'swal-button--cancel')"
        " and contains(normalize-space(.),'Cancel')]"
    )
    MSG_POPUP_CONFIRM = (
        By.XPATH,
        "//div[contains(@class,'swal-text')"
        " and contains(normalize-space(.),'Xóa sản phẩm này khỏi giỏ hàng')]"
    )

    MSG_EMPTY_CART = (
        By.XPATH,
        "//*[contains(normalize-space(.),'Chưa có sản phẩm nào trong giỏ hàng')]"
    )

    MSG_OUT_OF_STOCK = (By.CLASS_NAME, "swal-text")

    # Link SP đầu tiên – chỉ dùng làm tham chiếu, không dùng trực tiếp trong add_product
    FIRST_PRODUCT_LINK = (
        By.XPATH,
        "(//a[contains(@href,'Product/ProductDetail')])[2]"
    )

    BTN_ADD_TO_CART = (By.ID, "order-text")

    # Locator dùng cho TC-23
    LBL_ERROR_MESSAGE = (By.XPATH, "//*[contains(text(), 'Vui lòng nhập số lượng')]")
    COL_TOTAL_PRICE   = (By.CSS_SELECTOR, "td.product-subtotal span.amount")

    # ==========================================================
    # WAIT HELPERS  (giữ nguyên)
    # ==========================================================

    def wait_for_swal_appear(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.POPUP_SWAL)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_swal_disappear(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.POPUP_SWAL)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_cart_update(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.ROWS_CART_ITEM)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_empty_cart(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.MSG_EMPTY_CART)
            )
            return True
        except TimeoutException:
            return False

    def _wait_cart_page_ready(self, timeout=7):
        WebDriverWait(self.driver, timeout).until(
            lambda d:
                len(d.find_elements(*self.ROWS_CART_ITEM)) > 0
                or len(d.find_elements(*self.MSG_EMPTY_CART)) > 0
        )

    # ==========================================================
    # NAVIGATION
    # ==========================================================

    def open_cart(self, base_url):
        """Mở trang chủ → click icon giỏ hàng → chờ trang giỏ load xong."""
        self.open(base_url)
        self.safe_click(self.ICON_CART)
        self._wait_cart_page_ready()

    # ----------------------------------------------------------
    def add_product_to_cart(self, base_url, product_index=1):

        current = self.driver.current_url.lower()
        if "cart" in current or "order" in current:
            try:
                self.safe_click(self.BTN_CONTINUE_SHOPPING)
                WebDriverWait(self.driver, 7).until(
                    lambda d: "cart" not in d.current_url.lower()
                              and "order" not in d.current_url.lower()
                )
            except Exception:
                self.open(base_url)

        # ── B2 ────────────────────────────────────────────────
        if base_url.rstrip("/") not in self.driver.current_url:
            self.open(base_url)

        # ── B3 ────────────────────────────────────────────────
        target_product = (
            By.XPATH,
            f"(//a["
            f"contains(@href,'Product/ProductDetail')"
            f" and ("
            f"substring(@href,string-length(@href),1)='0'"
            f" or substring(@href,string-length(@href),1)='1'"
            f" or substring(@href,string-length(@href),1)='2'"
            f" or substring(@href,string-length(@href),1)='3'"
            f" or substring(@href,string-length(@href),1)='4'"
            f" or substring(@href,string-length(@href),1)='5'"
            f" or substring(@href,string-length(@href),1)='6'"
            f" or substring(@href,string-length(@href),1)='7'"
            f" or substring(@href,string-length(@href),1)='8'"
            f" or substring(@href,string-length(@href),1)='9'"
            f")])[{product_index}]"
        )
        WebDriverWait(self.driver, 7).until(EC.element_to_be_clickable(target_product))
        self.safe_click(target_product)

        # ── B4 ────────────────────────────────────────────────
        # Kiểm tra đã vào đúng trang chi tiết SP (URL phải chứa ProductDetail)
        WebDriverWait(self.driver, 10).until(
            lambda d: "ProductDetail" in d.current_url
                      or "productdetail" in d.current_url.lower()
        )
        # Nếu web trả về trang lỗi Server Error → raise ngay để ensure bắt được
        if "Server Error" in self.driver.title or "error" in self.driver.title.lower():
            raise RuntimeError(
                f"Web crash sau khi click SP index={product_index}. "
                f"URL: {self.driver.current_url}"
            )

        # ── B5 ────────────────────────────────────────────────
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_ADD_TO_CART)
        )
        self.safe_click(self.BTN_ADD_TO_CART)
        # Chờ SweetAlert thêm hàng thành công tự biến mất
        self.wait_for_swal_disappear(timeout=5)

        # ── B6 ────────────────────────────────────────────────
        btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.ICON_CART)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", btn
        )
        self.driver.execute_script("arguments[0].click();", btn)
        WebDriverWait(self.driver, 10).until(EC.url_contains("Cart/Orders"))
        self._wait_cart_page_ready()

    # ----------------------------------------------------------
    def ensure_cart_has_n_products(self, base_url, n=1):
    
        product_index = self.get_cart_item_count() + 1

        while self.get_cart_item_count() < n:
            before = self.get_cart_item_count()
            try:
                self.add_product_to_cart(base_url, product_index=product_index)
            except Exception:
                # SP này lỗi → thử SP tiếp theo
                pass

            after = self.get_cart_item_count()
            product_index += 1

            # Giới hạn tránh vòng lặp vô tận (thử tối đa 15 SP)
            if product_index > 15:
                break

        return self.get_cart_item_count()

    # ==========================================================
    # GETTERS  (giữ nguyên)
    # ==========================================================

    def get_cart_item_count(self):
        return len(self.driver.find_elements(*self.ROWS_CART_ITEM))

    def get_quantity_of(self, index=0):
        inputs = self.driver.find_elements(*self.INPUTS_QUANTITY)
        return int(inputs[index].get_attribute("value"))

    def get_swal_text(self):
        return self.get_text(self.MSG_SWAL_TEXT)

    def get_swal_title(self):
        return self.get_text(self.MSG_SWAL_TITLE)

    def get_total_price_text(self, index=0):
        elements = self.driver.find_elements(*self.COL_TOTAL_PRICE)
        return elements[index].text.strip() if len(elements) > index else ""

    def is_error_message_displayed(self):
        try:
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located(self.LBL_ERROR_MESSAGE)
            )
            return True
        except TimeoutException:
            return False

    # ==========================================================
    # ACTIONS  (giữ nguyên)
    # ==========================================================

    def set_quantity_of(self, index=0, value=""):
        inputs = self.driver.find_elements(*self.INPUTS_QUANTITY)
        el = inputs[index]
        el.clear()
        el.send_keys(str(value))

    def click_increase(self, index=0):
        btns = self.driver.find_elements(*self.BTNS_INCREASE)
        self.driver.execute_script("arguments[0].click();", btns[index])

    def click_decrease(self, index=0):
        btns = self.driver.find_elements(*self.BTNS_DECREASE)
        self.driver.execute_script("arguments[0].click();", btns[index])

    def click_remove(self, index=0):
        btns = self.driver.find_elements(*self.BTNS_REMOVE)
        self.driver.execute_script("arguments[0].click();", btns[index])

    def click_update_cart(self):
        self.safe_click(self.BTN_UPDATE_CART)

    def click_continue_shopping(self):
        self.safe_click(self.BTN_CONTINUE_SHOPPING)

    def click_order(self):
        self.safe_click(self.BTN_ORDER)

    def close_swal(self):
        """Đóng SweetAlert: chờ tự biến mất, nếu không thì nhấn ESC."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "swal-overlay"))
            )
        except Exception:
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    def confirm_delete(self):
        try:
            self.driver.switch_to.alert.accept()
        except NoAlertPresentException:
            self.safe_click(self.BTN_POPUP_OK)
        self.wait_for_swal_disappear()

    def cancel_delete(self):
        try:
            self.driver.switch_to.alert.dismiss()
        except NoAlertPresentException:
            self.safe_click(self.BTN_POPUP_CANCEL)
        self.wait_for_swal_disappear()

    # ==========================================================
    # STATE CHECKERS  (giữ nguyên)
    # ==========================================================

    def is_swal_visible(self):
        return self.check_visible(self.POPUP_SWAL)

    def is_empty_cart_visible(self):
        return self.check_visible(self.MSG_EMPTY_CART)

    def is_out_of_stock_visible(self):
        return self.check_visible(self.MSG_OUT_OF_STOCK)

    def is_confirm_popup_visible(self):
        try:
            self.driver.switch_to.alert
            return True
        except NoAlertPresentException:
            pass
        return self.check_visible(self.MSG_POPUP_CONFIRM)

    def is_btn_update_visible(self):
        return self.check_visible(self.BTN_UPDATE_CART)

    def is_btn_continue_visible(self):
        return self.check_visible(self.BTN_CONTINUE_SHOPPING)

    def is_btn_order_visible(self):
        return self.check_visible(self.BTN_ORDER)