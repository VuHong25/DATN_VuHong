
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage

# Số dòng mỗi trang – khớp với pageSize=10 trên server
PAGE_SIZE = 10


class InvoicePage(BasePage):

    # ==========================================================
    # LOCATORS – ĐĂNG NHẬP ADMIN
    # ==========================================================
    INPUT_ADMIN_USER = (By.ID, "username")
    INPUT_ADMIN_PASS = (By.ID, "password")
    BTN_ADMIN_LOGIN  = (By.XPATH, "//button[@type='submit']")

    # ==========================================================
    # LOCATORS – MENU QUẢN TRỊ
    # ==========================================================
    MENU_INVOICE = (By.XPATH, "//a[.//span[normalize-space()='Hóa đơn']]")

    # ==========================================================
    # LOCATORS – DANH SÁCH HÓA ĐƠN
    # ==========================================================
    INVOICE_ROWS = (By.XPATH,
        "//table[contains(@class,'table')]//tbody/tr[contains(@class,'group-info')]"
    )
    MSG_NO_INVOICE = (By.XPATH,
        "//*[contains(normalize-space(.),'Không có đơn hàng')]"
    )

    # ==========================================================
    # LOCATORS – PAGINATION
    # ==========================================================
    @staticmethod
    def page_link_locator(page_number: int) -> tuple:
        """
        Locator cho link số trang cụ thể trong pagination.
        """
        return (
            By.XPATH,
            f"//ul[contains(@class,'pagination')]"
            f"//a[normalize-space(text())='{page_number}']"
        )

    # ==========================================================
    # LOCATORS – NÚT 3 CHẤM
    # ==========================================================
    @staticmethod
    def btn_options_locator(row_index_on_page: int = 1) -> tuple:
        return (
            By.XPATH,
            f"(//table[contains(@class,'table')]//tbody"
            f"/tr[contains(@class,'group-info')])[{row_index_on_page}]"
            f"//button[contains(@class,'dropdown-toggle')]"
        )

    # ==========================================================
    # LOCATORS – ITEMS TRONG DROPDOWN
    # ==========================================================
    _XPATH_DETAIL_BTN = "//button[contains(@class,'infoBill')]"
    _XPATH_CANCEL_BTN = "//button[contains(@class,'change') and contains(@class,'text-danger')]"

    OPT_DETAIL = (By.XPATH, "//button[contains(@class,'infoBill')]")
    OPT_CANCEL = (By.XPATH,
        "//button[contains(@class,'change') and contains(@class,'text-danger')]"
    )

    # ==========================================================
    # LOCATORS – DROPDOWN TRẠNG THÁI
    # ==========================================================
    @staticmethod
    def dropdown_status_xpath(row_index_on_page: int = 1) -> str:
        """
        XPath cho <select> trạng thái ở dòng row_index_on_page trên trang hiện tại.
        """
        return (
            f"(//table[contains(@class,'table')]//tbody"
            f"/tr[contains(@class,'group-info')])[{row_index_on_page}]"
            f"//select[contains(@id,'hd-trangthai-update')]"
        )

    # ==========================================================
    # LOCATORS – MODAL CHI TIẾT
    # ==========================================================
    MODAL_DETAIL    = (By.ID, "popUp")
    BTN_MODAL_CLOSE = (By.ID, "cancelPopup")

    # ==========================================================
    # LOCATORS – SWEETALERT v1
    # ==========================================================
    SWAL_MODAL      = (By.XPATH, "//div[contains(@class,'swal-modal')]")
    SWAL_TITLE      = (By.XPATH, "//div[contains(@class,'swal-title')]")
    SWAL_TEXT       = (By.XPATH, "//div[contains(@class,'swal-text')]")
    SWAL_BTN_OK     = (By.XPATH, "//button[contains(@class,'swal-button--confirm')]")
    SWAL_BTN_CANCEL = (By.XPATH, "//button[contains(@class,'swal-button--cancel')]")

    # ==========================================================
    # LOCATORS – PHÍA KHÁCH HÀNG
    # ==========================================================
    CUSTOMER_ORDER_LINK = (By.XPATH,
        "//a[contains(normalize-space(.),'Đơn hàng của tôi')"
        " or contains(normalize-space(.),'Đơn hàng')"
        " or contains(@href,'Bill') or contains(@href,'Order')]"
        "[not(contains(@href,'Admin'))]"
    )
    CUSTOMER_ORDER_STATUS = (By.XPATH,
        "//table//tbody/tr[1]//select | "
        "//table//tbody/tr[1]//td[contains(@class,'status')]"
    )

    # ==========================================================
    # NAVIGATION
    # ==========================================================

    def open_admin_login(self, base_url: str):
        """Mở trang đăng nhập admin."""
        self.open(base_url + "Admin/Login")

    def login_admin(self, username: str, password: str):
    
        self.type_text(self.INPUT_ADMIN_USER, username)
        self.type_text(self.INPUT_ADMIN_PASS, password)
        btn = self.driver.find_element(*self.BTN_ADMIN_LOGIN)
        self.driver.execute_script("arguments[0].click();", btn)

        # Chờ trang phản hồi: đã ra khỏi login HOẶC có thông báo lỗi
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: (
                    "login" not in d.current_url.lower()
                    or len(d.find_elements(By.XPATH,
                        "//*[contains(normalize-space(.),'không được') or "
                        "contains(normalize-space(.),'không có quyền') or "
                        "contains(normalize-space(.),'không hợp lệ') or "
                        "contains(normalize-space(.),'Unauthorized') or "
                        "contains(normalize-space(.),'Invalid')]"
                    )) > 0
                )
            )
        except TimeoutException:
            pass  # Để test tự assert kết quả

    def dismiss_password_warning(self):
        """Không cần conftest đã tắt Chrome password manager."""
        pass

    def navigate_to_invoice_list(self):
        """Click menu Hóa đơn → /Admin/Bill. Chờ DOM load."""
        self.safe_click(self.MENU_INVOICE)
        WebDriverWait(self.driver, 10).until(
            lambda d: (
                len(d.find_elements(*self.INVOICE_ROWS)) > 0
                or len(d.find_elements(*self.MSG_NO_INVOICE)) > 0
                or "Bill" in d.current_url
            )
        )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    @staticmethod
    def calc_page_and_row(global_row_index: int, page_size: int = PAGE_SIZE):
       
        page_number = (global_row_index - 1) // page_size + 1
        row_on_page = (global_row_index - 1) % page_size + 1
        return page_number, row_on_page

    def navigate_to_page_for_row(self, global_row_index: int, page_size: int = PAGE_SIZE) -> int:
       
        page_number, row_on_page = self.calc_page_and_row(global_row_index, page_size)

        if page_number > 1:
            link_locator = self.page_link_locator(page_number)
            try:
                link = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable(link_locator)
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                self.driver.execute_script("arguments[0].click();", link)
                # Chờ trang mới load
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(d.find_elements(*self.INVOICE_ROWS)) > 0
                )
            except TimeoutException:
                # Fallback: mở trực tiếp URL với query param trang
                base = self.driver.current_url.split("?")[0]
                self.open(f"{base}?page={page_number}&pageSize={page_size}")
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(d.find_elements(*self.INVOICE_ROWS)) > 0
                )

        return row_on_page

    # ==========================================================
    # GETTERS
    # ==========================================================

    def get_invoice_row_count(self) -> int:
        """Đếm số dòng trên trang hiện tại."""
        return len(self.driver.find_elements(*self.INVOICE_ROWS))

    def get_status_by_row(self, row_index_on_page: int) -> str:
        """Đọc trạng thái đang được chọn ở dòng row_index_on_page (trên trang hiện tại)."""
        try:
            locator = (By.XPATH, self.dropdown_status_xpath(row_index_on_page))
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(locator)
            )
            return Select(el).first_selected_option.text.strip()
        except Exception:
            return ""

    def get_first_row_status(self) -> str:
        return self.get_status_by_row(1)

    def get_swal_title(self) -> str:
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.SWAL_TITLE)
            )
            return el.text.strip()
        except TimeoutException:
            return ""

    def get_swal_text(self) -> str:
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.SWAL_TEXT)
            )
            return el.text.strip()
        except TimeoutException:
            return ""

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_customer_order_status(self) -> str:
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.CUSTOMER_ORDER_STATUS)
            )
            if el.tag_name.lower() == "select":
                return Select(el).first_selected_option.text.strip()
            return el.text.strip()
        except Exception:
            return ""

    # ==========================================================
    # CHECKERS
    # ==========================================================

    def is_on_invoice_list_page(self) -> bool:
        has_table = len(self.driver.find_elements(*self.INVOICE_ROWS)) > 0
        has_empty  = len(self.driver.find_elements(*self.MSG_NO_INVOICE)) > 0
        url_ok     = "Bill" in self.driver.current_url
        return has_table or has_empty or url_ok

    def is_on_login_page(self) -> bool:
        """Kiểm tra đang ở trang đăng nhập (dùng cho TC-2)."""
        return "login" in self.driver.current_url.lower()

    def is_no_invoice_message_visible(self) -> bool:
        return self.check_visible(self.MSG_NO_INVOICE)

    def is_swal_visible(self) -> bool:
        return self.check_visible(self.SWAL_MODAL)

    def is_modal_detail_visible(self) -> bool:
        """
        Modal dùng inline style display:none / display:block.
        Trả về True khi KHÔNG có 'display: none'.
        """
        try:
            el = self.driver.find_element(*self.MODAL_DETAIL)
            style = el.get_attribute("style") or ""
            return "display: none" not in style and "display:none" not in style
        except Exception:
            return False

    # ==========================================================
    # ACTIONS
    # ==========================================================

    def click_options_btn(self, row_index_on_page: int = 1):
        
        locator = self.btn_options_locator(row_index_on_page)
        el = WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located(locator)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

        # Chờ dropdown-menu có class 'show'
        menu_show_xpath = (
            f"(//table[contains(@class,'table')]//tbody"
            f"/tr[contains(@class,'group-info')])[{row_index_on_page}]"
            f"//div[contains(@class,'dropdown-menu') and contains(@class,'show')]"
        )
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.XPATH, menu_show_xpath)) > 0
            )
        except TimeoutException:
            WebDriverWait(self.driver, 5).until(
                lambda d: any(
                    b.is_displayed()
                    for b in d.find_elements(By.XPATH, self._XPATH_DETAIL_BTN)
                )
            )

    def click_view_detail(self):
        """Click button.infoBill visible → chờ modal #popUp hiện ra."""
        btns = self.driver.find_elements(By.XPATH, self._XPATH_DETAIL_BTN)
        visible = [b for b in btns if b.is_displayed()]
        if not visible:
            raise TimeoutException(
                "Không thấy nút 'Chi tiết hóa đơn'. Dropdown chưa mở hoặc locator sai."
            )
        self.driver.execute_script("arguments[0].click();", visible[0])
        WebDriverWait(self.driver, 8).until(lambda d: self.is_modal_detail_visible())

    def click_close_detail_modal(self):
        """Click div#cancelPopup để đóng modal."""
        el = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.BTN_MODAL_CLOSE)
        )
        self.driver.execute_script("arguments[0].click();", el)
        WebDriverWait(self.driver, 5).until(
            lambda d: not self.is_modal_detail_visible()
        )

    def click_cancel_order(self):
        """Click button.change.text-danger visible → chờ SweetAlert."""
        btns = self.driver.find_elements(By.XPATH, self._XPATH_CANCEL_BTN)
        visible = [b for b in btns if b.is_displayed()]
        if not visible:
            raise TimeoutException(
                "Không thấy nút 'Hủy đơn hàng'. "
                "Dropdown chưa mở hoặc đơn đã bị hủy (không hiển thị nút này)."
            )
        self.driver.execute_script("arguments[0].click();", visible[0])
        WebDriverWait(self.driver, 8).until(
            EC.visibility_of_element_located(self.SWAL_MODAL)
        )

    def click_swal_ok(self):
        el = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.SWAL_BTN_OK)
        )
        self.driver.execute_script("arguments[0].click();", el)
        WebDriverWait(self.driver, 8).until(
            lambda d: not self.check_visible(self.SWAL_MODAL)
        )

    def click_swal_cancel(self):
        el = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.SWAL_BTN_CANCEL)
        )
        self.driver.execute_script("arguments[0].click();", el)
        WebDriverWait(self.driver, 5).until(
            lambda d: not self.check_visible(self.SWAL_MODAL)
        )

    def select_status(self, status_text: str, row_index_on_page: int = 1):
        
        locator = (By.XPATH, self.dropdown_status_xpath(row_index_on_page))
        el = WebDriverWait(self.driver, 8).until(
            EC.element_to_be_clickable(locator)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        Select(el).select_by_visible_text(status_text)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", el)
        WebDriverWait(self.driver, 8).until(
            lambda d: status_text in d.page_source
        )

    def wait_for_status_update(self, expected_status: str, timeout: int = 8) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: expected_status.lower() in d.page_source.lower()
            )
            return True
        except TimeoutException:
            return False

    def navigate_to_customer_orders(self, base_url: str):
        """Điều hướng sang trang đơn hàng khách hàng để kiểm tra đồng bộ."""
        if "Admin" in self.driver.current_url:
            self.open(base_url)
        try:
            link = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.CUSTOMER_ORDER_LINK)
            )
            self.driver.execute_script("arguments[0].click();", link)
            WebDriverWait(self.driver, 8).until(
                lambda d: any(kw in d.current_url
                              for kw in ["Bill", "bill", "Order", "order"])
            )
        except Exception:
            for path in ["Bill/ListBills", "Order/Index", "Bill"]:
                try:
                    self.open(base_url + path)
                    WebDriverWait(self.driver, 3).until(
                        lambda d: len(d.find_elements(By.XPATH, "//table//tbody/tr")) > 0
                    )
                    return
                except Exception:
                    continue
