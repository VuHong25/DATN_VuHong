

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.cart_page      import CartPage
from pages.order_page     import OrderPage
from pages.login_page_new import LoginPage
from data.test_data_order import (
    VALID_USER, VALID_PASSWORD,
    DEFAULT_RECEIVER, CHANGED_RECEIVER,
    EMPTY_FIELD_DATA, ORDER_SUCCESS_DATA,
    ORDER_EMPTY_CART,
)
from conftest import base_url


# ==============================================================
# HELPER dùng chung: đảm bảo giỏ có n SP rồi click Đặt hàng
# ==============================================================

def _go_to_checkout(driver, n_products=1):
    """
      1. Mở giỏ hàng
      2. Đảm bảo có đủ n SP (tận dụng CartPage.ensure_cart_has_n_products)
      3. Click nút Đặt hàng → vào trang checkout
      4. Chờ trang checkout load

    Trả về (cart, order) để test tiếp tục dùng.
    """
    cart  = CartPage(driver)
    order = OrderPage(driver)

    cart.open_cart(base_url)
    cart.ensure_cart_has_n_products(base_url, n=n_products)
    order.click_order_button()
    order.is_on_checkout_page()   # chờ trang checkout xuất hiện

    return cart, order


# ==============================================================
# NHÓM: ACCESS RIGHT
# ==============================================================

class TestOrderAccessRight:

    def test_tc1_order_without_login_redirects_to_login(self, driver):
       
        cart  = CartPage(driver)
        order = OrderPage(driver)

        # Thêm SP vào giỏ (không cần đăng nhập)
        cart.open_cart(base_url)
        cart.add_product_to_cart(base_url, product_index=1)

        # Click Đặt hàng
        order.click_order_button()

        # Kỳ vọng: redirect sang trang đăng nhập
        assert order.is_redirected_to_login(), \
            "TC-1: Chưa đăng nhập → click Đặt hàng phải redirect đến trang đăng nhập"

    def test_tc2_order_after_login_reaches_checkout(self, driver):
      
        cart  = CartPage(driver)
        order = OrderPage(driver)
        login = LoginPage(driver)

        # Bước 1: Thêm SP vào giỏ (guest session)
        cart.open_cart(base_url)
        cart.add_product_to_cart(base_url, product_index=1)

        # Bước 2: Click Đặt hàng → hệ thống redirect sang login
        order.click_order_button()
        assert order.is_redirected_to_login(), \
            "TC-2 bước trung gian: phải redirect đến login khi chưa đăng nhập"

        # Bước 3: Đăng nhập
        login.login(VALID_USER, VALID_PASSWORD)
        WebDriverWait(driver, 10).until(
            lambda d: "login" not in d.current_url.lower()
        )

        # Bước 4: Về giỏ hàng → click Đặt hàng lần 2
        cart.open_cart(base_url)
        cart.ensure_cart_has_n_products(base_url, n=1)
        order.click_order_button()

        # Kỳ vọng: vào được trang checkout
        assert order.is_on_checkout_page(), \
            "TC-2: Sau khi đăng nhập, phải vào được trang thanh toán"



# ==============================================================
# NHÓM: VALIDATION
# ==============================================================

class TestOrderValidation:

    def test_tc7_keep_default_info_order_success(self, logged_in_driver):
        
        driver = logged_in_driver
        cart, order = _go_to_checkout(driver, n_products=1)

        # Không thay đổi gì – giữ nguyên mặc định
        order.click_dat_hang()

        assert order.is_order_placed_successfully(), \
            "TC-7: Giữ thông tin mặc định → đặt hàng phải thành công"

    def test_tc8_change_receiver_info_order_success(self, logged_in_driver):
       
        driver = logged_in_driver
        cart, order = _go_to_checkout(driver, n_products=1)

        order.fill_receiver_info(
            ho_ten  = CHANGED_RECEIVER["ho_ten"],
            sdt     = CHANGED_RECEIVER["sdt"],
            dia_chi = CHANGED_RECEIVER["dia_chi"],
            ghi_chu = CHANGED_RECEIVER["ghi_chu"],
        )
        order.click_dat_hang()

        assert order.is_order_placed_successfully(), \
            "TC-8: Thay đổi thông tin nhận hàng → đặt hàng phải thành công"

    @pytest.mark.parametrize(
        "tc_id, ho_ten, sdt, dia_chi, ghi_chu, field_to_check, mo_ta",
        EMPTY_FIELD_DATA,
        ids=[d[0] for d in EMPTY_FIELD_DATA]
    )
    def test_tc9_empty_required_field_html5_error(
        self, logged_in_driver,
        tc_id, ho_ten, sdt, dia_chi, ghi_chu, field_to_check, mo_ta
    ):
        
        driver = logged_in_driver
        cart, order = _go_to_checkout(driver, n_products=1)

        # None = giữ nguyên mặc định, "" = xóa trắng (trigger required)
        order.fill_receiver_info(
            ho_ten  = ho_ten,
            sdt     = sdt,
            dia_chi = dia_chi,
            ghi_chu = ghi_chu,
        )

        # Click Đặt hàng (HTML5 sẽ chặn submit)
        order.click_dat_hang()

        # Ánh xạ tên field → locator thực tế
        field_locator_map = {
            "ho_ten"  : order.INPUT_HO_TEN,
            "sdt"     : order.INPUT_SDT,
            "dia_chi" : order.INPUT_DIA_CHI,
        }
        target_locator = field_locator_map[field_to_check]

        # Kiểm tra field bị HTML5 đánh dấu invalid
        assert order.is_field_invalid_html5(target_locator), \
            f"[{tc_id}] {mo_ta} – Field '{field_to_check}' phải invalid (required)"

        # Vẫn đang ở trang checkout (không submit được)
        assert order.is_on_checkout_page(), \
            f"[{tc_id}] Không được chuyển trang khi bỏ trống field bắt buộc"


# ==============================================================
# NHÓM: BIZ – NGHIỆP VỤ
# ==============================================================

class TestOrderBiz:

    @pytest.mark.parametrize(
        "tc_id, mo_ta",
        ORDER_SUCCESS_DATA,
        ids=[d[0] for d in ORDER_SUCCESS_DATA]
    )
    def test_tc10_place_order_success_cart_becomes_empty(
        self, logged_in_driver, tc_id, mo_ta
    ):
    
        driver = logged_in_driver
        cart, order = _go_to_checkout(driver, n_products=1)

        order.click_dat_hang()

        assert order.is_order_placed_successfully(), \
            f"[{tc_id}] Đặt hàng phải thành công và chuyển trang"

        cart.open_cart(base_url)
        assert cart.is_empty_cart_visible(), \
            f"[{tc_id}] Sản phẩm phải biến mất khỏi giỏ hàng sau khi đặt thành công"

    def test_tc11_order_empty_cart_not_allowed(self, logged_in_driver):
      
        driver = logged_in_driver
        cart  = CartPage(driver)
        order = OrderPage(driver)

        # Mở giỏ → xóa hết SP nếu còn
        cart.open_cart(base_url)
        while cart.get_cart_item_count() > 0:
            cart.click_remove(index=0)
            if cart.wait_for_swal_appear(timeout=3):
                cart.confirm_delete()
                cart.wait_for_swal_disappear(timeout=5)

        # Xác nhận giỏ rỗng (precondition)
        assert cart.is_empty_cart_visible(), \
            "TC-11 Precondition: giỏ hàng phải rỗng trước khi test"

        btn_present = order.is_order_button_present()

        if btn_present:
            # Nút hiện → click → không được chuyển sang checkout
            order.click_order_button()
            assert not order.is_on_checkout_page(), \
                "TC-11: Giỏ rỗng → click Đặt hàng không được vào trang thanh toán"
        else:
            # Nút bị ẩn hoàn toàn → pass 
            assert True, "TC-11: Giỏ rỗng → nút Đặt hàng bị ẩn đúng thiết kế"
