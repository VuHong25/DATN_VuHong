
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class OrderPage(BasePage):

    # ==========================================================
    # LOCATORS – Trang giỏ hàng /Cart/Orders
    # ==========================================================

    # Icon giỏ hàng trên header (By.ID từ order_page.py – đúng với HTML thực)
    ICON_CART = (By.ID, "product-count")

    # Các dòng sản phẩm trong bảng giỏ hàng
    ROWS_CART_ITEM = (By.XPATH, "//tr[contains(@class,'cart_item')]")

    # Nút "Đặt hàng" ở cuối trang giỏ hàng → click để vào checkout
    BTN_ORDER_CART = (
        By.XPATH,
        "//div[contains(@class,'wc-proceed-to-checkout')]//a"
    )

    # Thông báo giỏ rỗng
    MSG_EMPTY_CART = (
        By.XPATH,
        "//*[contains(normalize-space(.),'Chưa có sản phẩm nào trong giỏ hàng')]"
    )

    # ==========================================================
    # LOCATORS – Trang Checkout /Cart/CheckOut
    # ==========================================================

    INPUT_HO_TEN  = (By.NAME, "hotennguoinhan")
    INPUT_SDT     = (By.NAME, "sodienthoainhan")
    INPUT_DIA_CHI = (By.NAME, "diachinhan")
    INPUT_GHI_CHU = (By.ID,   "checkout-mess")   # Ghi chú (không bắt buộc)

    # Nút submit đặt hàng trên trang checkout
    BTN_DAT_HANG = (
        By.XPATH,
        "//input[@type='submit' and contains(@value,'Đặt hàng')]"
    )

    # ==========================================================
    # LOCATORS – Trang đăng nhập (redirect khi chưa login)
    # ==========================================================

    LOGIN_FORM = (By.XPATH, "//input[@name='username']")
    # ==========================================================
    # METHODS – Navigation
    # ==========================================================

    def open_cart_direct(self, base_url: str):
      
        self.open(base_url + "Cart/Order")
        WebDriverWait(self.driver, 10).until(
            lambda d:
                len(d.find_elements(*self.ROWS_CART_ITEM)) > 0
                or len(d.find_elements(*self.MSG_EMPTY_CART)) > 0
        )

    def open_cart_via_icon(self, base_url: str):
       
        self.open(base_url)
        self.safe_click(self.ICON_CART)

    def dismiss_password_popup(self):
      
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    # ==========================================================
    # METHODS – Thao tác trên trang giỏ hàng
    # ==========================================================

    def click_order_button(self):
      
        self.safe_click(self.BTN_ORDER_CART)

    # ==========================================================
    # METHODS – Thao tác trên trang Checkout
    # ==========================================================

    def fill_receiver_info(self, ho_ten=None, sdt=None, dia_chi=None, ghi_chu=None):
        """
        Điền thông tin nhận hàng trên trang checkout.
        """
        fields = [
            (self.INPUT_HO_TEN,  ho_ten),
            (self.INPUT_SDT,     sdt),
            (self.INPUT_DIA_CHI, dia_chi),
            (self.INPUT_GHI_CHU, ghi_chu),
        ]
        for locator, value in fields:
            if value is None:
                continue      # Giữ nguyên mặc định
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(locator)
                )
                el.clear()
                if value != "":
                    el.send_keys(value)
            except TimeoutException:
                pass          
    def click_dat_hang(self):
        self.safe_click(self.BTN_DAT_HANG)

    # ==========================================================
    # STATE CHECKERS
    # ==========================================================

    def get_cart_item_count(self) -> int:
        """Đếm số dòng sản phẩm hiện có trong bảng giỏ hàng."""
        return len(self.driver.find_elements(*self.ROWS_CART_ITEM))

    def is_empty_cart_visible(self) -> bool:
        """Kiểm tra thông báo giỏ rỗng đang hiển thị."""
        return self.check_visible(self.MSG_EMPTY_CART)

    def is_redirected_to_login(self) -> bool:
     
        try:
            WebDriverWait(self.driver, 7).until(
                lambda d:
                    "login" in d.current_url.lower()
                    or len(d.find_elements(*self.LOGIN_FORM)) > 0
            )
            return True
        except TimeoutException:
            return False

    def is_on_checkout_page(self) -> bool:
        """
        Kiểm tra đang ở trang /Cart/CheckOut.
        """
        try:
            WebDriverWait(self.driver, 7).until(
                lambda d: "checkout" in d.current_url.lower()
            )
            return True
        except TimeoutException:
            return False

    def is_order_placed_successfully(self) -> bool:
      
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d:
                    "checkout" not in d.current_url.lower()
                    and "cart" not in d.current_url.lower()
            )
            return True
        except TimeoutException:
            return False

    def is_order_button_present(self) -> bool:
       
        return len(self.driver.find_elements(*self.BTN_ORDER_CART)) > 0

    def is_field_invalid_html5(self, locator) -> bool:
       
        el = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].focus();", el)
        return not self.driver.execute_script(
            "return arguments[0].checkValidity();", el
        )

    def get_ho_ten_value(self) -> str:
        try:
            return (
                self.driver.find_element(*self.INPUT_HO_TEN)
                    .get_attribute("value") or ""
            )
        except Exception:
            return ""

    def get_sdt_value(self) -> str:
        """Lấy giá trị hiện tại của field Số điện thoại."""
        try:
            return (
                self.driver.find_element(*self.INPUT_SDT)
                    .get_attribute("value") or ""
            )
        except Exception:
            return ""

    def get_dia_chi_value(self) -> str:
        """Lấy giá trị hiện tại của field Địa chỉ."""
        try:
            return (
                self.driver.find_element(*self.INPUT_DIA_CHI)
                    .get_attribute("value") or ""
            )
        except Exception:
            return ""







