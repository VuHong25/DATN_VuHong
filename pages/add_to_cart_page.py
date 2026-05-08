

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from pages.product_page import ProductDetailPage
from selenium.webdriver.common.by import By

class AddToCartPage(ProductDetailPage):
    """
    Page Object cho chức năng Thêm Sản Phẩm Vào Giỏ Hàng.
    Kế thừa ProductDetailPage: dùng lại toàn bộ locators, getters, checkers,
    navigation. Chỉ bổ sung các action đặc thù: set_quantity, click_add_to_cart.
    """

    # ==========================================================
    # ACTIONS – đặc thù cho thêm vào giỏ
    # ==========================================================

    def set_quantity(self, value: int):
        """
        Nhập số lượng vào ô input (id='modal-soluong').
        Dùng cho TC-15: nhập SL > tồn kho.

        """
        INPUT_QUANTITY = ("id", "modal-soluong")
        try:
            
            locator = (By.ID, "modal-soluong")
            el = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(locator)
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



















# # ============================================================
# # FILE: pages/category_page.py
# # MỤC ĐÍCH: Page Object Model cho chức năng Xem danh mục sản phẩm
# #
# # LUỒNG THỰC TẾ:
# #   Trang chủ → HOVER vào "Sản phẩm" trên menu
# #   → Dropdown xuất hiện với danh sách danh mục
# #   → Nếu không có danh mục → hiển thị "Chưa có danh mục nào!"
# #   Không yêu cầu đăng nhập.
# #
# # GHI CHÚ TÍCH HỢP:
# #   - Locators (MENU_SAN_PHAM, CATEGORY_ITEMS, MSG_NO_CATEGORY) lấy từ code gốc
# #     của bạn vì bạn biết đúng class CSS thực tế ("ht-dropdown")
# #   - Kế thừa BasePage (giữ nguyên như code gốc của bạn)
# #   - Bổ sung từ file cũ: login(), _scroll_to(), is_error_message_displayed(),
# #     get_current_url(), is_menu_san_pham_visible/enabled (đã có sẵn trong code bạn)
# #   - click_menu_san_pham đổi tên thành hover_menu_san_pham cho rõ nghĩa
# #     (giữ logic hover của bạn, thêm scroll_to để tránh bị che)
# # ============================================================

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
# from pages.base_page import BasePage


# class CategoryPage(BasePage):

#     # ---- Locators (giữ nguyên của bạn — đúng với HTML thực tế) ----

#     MENU_SAN_PHAM = (By.XPATH, "//a[normalize-space()='Sản phẩm']")

#     # Class "ht-dropdown" lấy từ code bạn — chính xác hơn XPath đoán mò
#     CATEGORY_ITEMS = (By.XPATH, "//ul[contains(@class,'ht-dropdown')]//a")

#     MSG_NO_CATEGORY = (
#         By.XPATH,
#         "//*[contains(normalize-space(.),'Chưa có danh mục nào!')]",
#     )

#     # Thông báo lỗi hệ thống (bổ sung từ file cũ)
#     MSG_ERROR = (By.XPATH, "//*[contains(normalize-space(.),'Lỗi hệ thống')]")

#     # ---- Setup ----

#     def open_home(self, base_url: str):
#         self.open(base_url)

#     def login(self, base_url: str, username: str, password: str):
#         """Đăng nhập (tái sử dụng LoginPage có sẵn)."""
#         from pages.login_page_new import LoginPage
#         lp = LoginPage(self.driver)
#         lp.open_login_page(base_url)
#         lp.login(username, password)
#         WebDriverWait(self.driver, 10).until(
#             lambda d: base_url.rstrip("/") in d.current_url
#             or "Home" in d.current_url
#             or d.current_url == base_url
#         )
#         # 🔥 QUAN TRỌNG: chờ menu render xong
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located(self.MENU_SAN_PHAM)
#         )

#     # ---- Actions ----
#     def hover_menu_san_pham(self):
#     # """
#     # Hover vào menu 'Sản phẩm' → dropdown danh mục xuất hiện.
#     # Fix stale element bằng retry.
#     # """
#         for _ in range(2):  # thử lại tối đa 2 lần
#             try:
#                 menu = WebDriverWait(self.driver, 10).until(
#                     EC.visibility_of_element_located(self.MENU_SAN_PHAM)
#                 )

#                 # scroll
#                 self.driver.execute_script(
#                     "arguments[0].scrollIntoView({block:'center'});",
#                     menu,
#                 )

#                 # hover
#                 ActionChains(self.driver).move_to_element(menu).perform()

#                 # wait dropdown
#                 WebDriverWait(self.driver, 5).until(
#                     lambda d:
#                         len(d.find_elements(*self.CATEGORY_ITEMS)) > 0
#                         or len(d.find_elements(*self.MSG_NO_CATEGORY)) > 0
#                 )
#                 return

#             except Exception as e:
#                 from selenium.common.exceptions import StaleElementReferenceException
#                 if isinstance(e, StaleElementReferenceException):
#                     continue  # retry
#                 raise
#     # def hover_menu_san_pham(self):
#     #     """
#     #     Hover vào menu 'Sản phẩm' → dropdown danh mục xuất hiện.
#     #     Thêm scroll_to để tránh menu bị che khuất bởi header/sticky bar.
#     #     """
#     #     menu = WebDriverWait(self.driver, 10).until(
#     #         EC.presence_of_element_located(self.MENU_SAN_PHAM)
#     #     )
#     #     # Scroll đến menu trước khi hover (tránh bị overlay che)
#     #     self.driver.execute_script(
#     #         "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
#     #         menu,
#     #     )
#     #     ActionChains(self.driver).move_to_element(menu).perform()

#     #     # Chờ dropdown xuất hiện (có item HOẶC thông báo rỗng)
#     #     try:
#     #         WebDriverWait(self.driver, 5).until(
#     #             lambda d:
#     #                 len(d.find_elements(*self.CATEGORY_ITEMS)) > 0
#     #                 or len(d.find_elements(*self.MSG_NO_CATEGORY)) > 0
#     #         )
#     #     except TimeoutException:
#     #         pass  # Sẽ được xử lý ở tầng test

#     # ---- Verifications ----

#     def get_category_count(self) -> int:
#         """Số lượng danh mục hiển thị trong dropdown."""
#         return len(self.driver.find_elements(*self.CATEGORY_ITEMS))

#     def get_category_names(self) -> list:
#         """Danh sách tên các danh mục hiển thị (lọc tên rỗng)."""
#         items = self.driver.find_elements(*self.CATEGORY_ITEMS)
#         return [el.text.strip() for el in items if el.text.strip()]

#     def is_no_category(self) -> bool:
#         """
#         True khi KHÔNG có danh mục nào VÀ thông báo 'Chưa có danh mục nào!' xuất hiện.
#         Dùng khi không thể xóa danh mục trong DB để test TC-8.
#         (Giữ nguyên logic của bạn)
#         """
#         categories = self.driver.find_elements(*self.CATEGORY_ITEMS)
#         no_msg = self.driver.find_elements(*self.MSG_NO_CATEGORY)
#         return len(categories) == 0 and len(no_msg) > 0

#     def is_dropdown_visible(self) -> bool:
#         """
#         True nếu dropdown có ít nhất 1 danh mục HOẶC thông báo rỗng.
#         Dùng để kiểm tra hover đã mở dropdown thành công.
#         """
#         return self.get_category_count() > 0 or self.is_no_category()

#     def is_error_message_displayed(self) -> bool:
#         """True nếu thông báo 'Lỗi hệ thống' xuất hiện."""
#         try:
#             el = WebDriverWait(self.driver, 5).until(
#                 EC.visibility_of_element_located(self.MSG_ERROR)
#             )
#             return el.is_displayed()
#         except Exception:
#             return False

#     def is_menu_san_pham_visible(self) -> bool:
#         return self.check_visible(self.MENU_SAN_PHAM)

#     def is_menu_san_pham_enabled(self) -> bool:
#         try:
#             el = self.driver.find_element(*self.MENU_SAN_PHAM)
#             return el.is_enabled()
#         except Exception:
#             return False

#     def get_current_url(self) -> str:
#         return self.driver.current_url

        
# #     # ============================================================
# # # FILE: pages/category_page.py
# # # MỤC ĐÍCH: Page Object Model cho chức năng Xem danh mục sản phẩm
# # # LUỒNG: Trang chủ → hover "Sản phẩm" trên menu
# # #         → hiển thị tất cả danh mục đang có
# # #         → nếu không có danh mục → hiển thị "Chưa có danh mục nào!"
# # # ============================================================
