
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage


class RegisterPage(BasePage):
    """
    Đại diện cho trang Đăng ký.
    """

    # ------------------------------------------------------------------
    # LOCATORS – Điều chỉnh selector cho khớp với HTML thực tế của web
    # ------------------------------------------------------------------
    # Menu navigation
    MENU_TAI_KHOAN   = (By.XPATH, "//a[contains(text(),'Tài khoản') or contains(@class,'account')]")
    DROPDOWN_DANG_KY = (By.XPATH, "//a[contains(text(),'Đăng ký')]")

    INPUT_HO_TEN      = (By.ID, "HoTen")       
    INPUT_SDT         = (By.ID, "SoDienThoai")
    INPUT_DIA_CHI     = (By.ID, "DiaChi")
    INPUT_EMAIL       = (By.ID, "Email")
    INPUT_NGAY_SINH   = (By.ID, "NgaySinh")
    INPUT_TAI_KHOAN   = (By.ID, "TenDangNhap")
    INPUT_MAT_KHAU    = (By.ID, "pwd")
    INPUT_XAC_NHAN_MK = (By.ID, "pwd-confirm")

    RADIO_NAM = (By.ID, "Male")
    RADIO_NU = (By.ID, "Female")

    # Button đăng ký
    BTN_DANG_KY = (By.CLASS_NAME, "return-customer-btn")
   
    # Thông báo lỗi từ server (span)
    msg_error = (By.ID, "error-message")

    HOME_INDICATOR = (By.ID, "slider")

    # ------------------------------------------------------------------
    # WAIT TIMEOUT – tách ra để dễ chỉnh khi web chậm
    # ------------------------------------------------------------------
    TIMEOUT_SHORT  = 5    # dùng cho thao tác nhỏ
    TIMEOUT_MEDIUM = 7  # mặc định
    TIMEOUT_LONG   = 10   # chờ redirect sau submit

    # ------------------------------------------------------------------
    # NAVIGATION – Mở trang đăng ký từ menu
    # ------------------------------------------------------------------

    def open_register_page(self, base_url: str):
        """
        Mở web → click Tài khoản → click Đăng ký.
        """
        self.open(base_url)
        # self._handle_ssl_warning()
        self._click_menu_to_register()

    def _click_menu_to_register(self):
        from selenium.webdriver.common.action_chains import ActionChains

        # Chờ menu Tài khoản xuất hiện
        tai_khoan_menu = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.presence_of_element_located(self.MENU_TAI_KHOAN)
        )
        # Hover để dropdown xuất hiện
        ActionChains(self.driver).move_to_element(tai_khoan_menu).perform()

        # Chờ và click 'Đăng ký' trong dropdown
        dang_ky_link = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.element_to_be_clickable(self.DROPDOWN_DANG_KY)
        )
        dang_ky_link.click()

        # Chờ form đăng ký load xong (kiểm tra input họ tên xuất hiện)
        WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.presence_of_element_located(self.INPUT_HO_TEN)
        )
   
    # ------------------------------------------------------------------
    # FORM FILLING – Điền từng trường
    # ------------------------------------------------------------------

    def fill_ho_ten(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_HO_TEN)
        )
        el.clear()
        if value:
            el.send_keys(value)

    def fill_so_dien_thoai(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_SDT)
        )
        el.clear()
        if value:
            el.send_keys(value)

    def fill_dia_chi(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_DIA_CHI)
        )
        el.clear()
        if value:
            el.send_keys(value)

    def fill_email(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_EMAIL)
        )
        el.clear()
        if value:
            el.send_keys(value)

    def fill_ngay_sinh(self, value: str):
        """
        Điền ngày sinh.
        Format: "YYYY-MM-DD" cho type="date", hoặc "DD/MM/YYYY" nếu là text.
        """
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_NGAY_SINH)
        )
        el.clear()
        if value:
            # Thử send_keys trước
            # el.send_keys(value)
            # Nếu web dùng type="date", cần format YYYY-MM-DD
            # Uncomment dòng dưới nếu send_keys không hoạt động:
            self.driver.execute_script(
                "arguments[0].value = arguments[1]", el, value
            )

    def select_gioi_tinh(self, gioi_tinh: str):
        """
        Chọn giới tính.
        gioi_tinh: "nam" hoặc "nu" (không phân biệt hoa/thường)
        """
        if gioi_tinh.lower() in ("nu", "nữ", "female"):
            self.safe_click(self.RADIO_NAM)
        else:
            self.safe_click(self.RADIO_NU)

    def fill_tai_khoan(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_TAI_KHOAN)
        )
        el.clear()
        if value:
            el.send_keys(value)

    def fill_mat_khau(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_MAT_KHAU)
        )
        el.clear()
        if value:
            el.send_keys(value)

    def fill_xac_nhan_mat_khau(self, value: str):
        el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
            EC.visibility_of_element_located(self.INPUT_XAC_NHAN_MK)
        )
        el.clear()
        if value:
            el.send_keys(value)

    # ------------------------------------------------------------------
    # SUBMIT FORM
    # ------------------------------------------------------------------

    def click_dang_ky(self):
       
        # self.safe_click(self.BTN_DANG_KY)
        try:
            el = WebDriverWait(self.driver, self.TIMEOUT_MEDIUM).until(
                EC.element_to_be_clickable(self.BTN_DANG_KY)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
        except Exception:
            ### FIX: fallback JS click
            el = self.driver.find_element(*self.BTN_DANG_KY)
            self.driver.execute_script("arguments[0].click();", el)

    # ------------------------------------------------------------------
    # COMPLETE FORM – Điền toàn bộ form một lần
    # ------------------------------------------------------------------

    def fill_form(self, ho_ten="", sdt="", dia_chi="", gioi_tinh="nu",
                  email="", ngay_sinh="", tai_khoan="",
                  mat_khau="", xac_nhan_mk=""):
       
        self.fill_ho_ten(ho_ten)
        self.fill_so_dien_thoai(sdt)
        self.fill_dia_chi(dia_chi)
        self.select_gioi_tinh(gioi_tinh)
        self.fill_email(email)
        self.fill_ngay_sinh(ngay_sinh)
        self.fill_tai_khoan(tai_khoan)
        self.fill_mat_khau(mat_khau)
        self.fill_xac_nhan_mat_khau(xac_nhan_mk)

    # ------------------------------------------------------------------
    # ASSERTION HELPERS – Kiểm tra kết quả sau khi submit
    # ------------------------------------------------------------------

    def get_html5_validation_message(self, locator) -> str:
        
        el = self.driver.find_element(*locator)
        return self.driver.execute_script(
            "return arguments[0].validationMessage;", el
        )


    def get_span_error_text(self, timeout: int = None) -> str:
       
        t = timeout or self.TIMEOUT_LONG
        error_locators = [
            self.msg_error
        ]
        for locator in error_locators:
            try:
                el = WebDriverWait(self.driver, t).until(
                    EC.visibility_of_element_located(locator)
                )
                text = el.text.strip()
                if text:
                    return text
            except TimeoutException:
                continue
        return ""

    def wait_for_home_page(self, timeout: int = None) -> bool:
       
        t = timeout or self.TIMEOUT_LONG

        try:
            WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(self.HOME_INDICATOR)
            )
            return True
        except TimeoutException:
            return False
        

    def is_on_home_page(self) -> bool:
        current_url = self.driver.current_url.lower()
        return (
            "signup" not in current_url
            and "dang-ky" not in current_url
        )

    def get_current_url(self) -> str:
        return self.driver.current_url

    # ------------------------------------------------------------------
    # UTILITY – Scroll tới input để tránh bị che khuất bởi header
    # ------------------------------------------------------------------

    def scroll_to_submit_button(self):
        try:
            el = self.driver.find_element(*self.BTN_DANG_KY)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
        except NoSuchElementException:
            pass



