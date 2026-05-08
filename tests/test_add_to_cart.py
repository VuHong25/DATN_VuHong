import pytest

from pages.add_to_cart_page import AddToCartPage
from conftest import base_url, LOGIN_PASSWORD, LOGIN_USERNAME
from data.test_data_add_to_cart import (
    # base_url,
    PRODUCT_ADD_TO_CART_SUCCESS,
    PRODUCT_ADD_TO_CART_OUT_OF_STOCK,
    PRODUCT_ADD_TO_CART_OUT_OF_SIZE,
    PRODUCT_EXCEED_QUANTITY,
    SWAL_APPEAR_TIMEOUT,
    SWAL_DISAPPEAR_TIMEOUT,
)

class TestAddToCartAccessRight:

    def test_tc01_add_to_cart_not_logged_in(self, driver):
        """TC-1: Chưa đăng nhập → vẫn thêm được vào giỏ."""
        page = AddToCartPage(driver)
        page.navigate_by_click_on_homepage(base_url, product_index=1)

        result = page.click_add_to_cart_and_wait_swal()

        assert result, (
            "TC-1 FAIL: Chưa đăng nhập nhưng không thêm được vào giỏ hàng."
        )

    def test_tc02_add_to_cart_logged_in(self, logged_in_driver):
        """TC-2: Đã đăng nhập → vẫn thêm được vào giỏ."""
        page = AddToCartPage(logged_in_driver)
        page.navigate_by_click_on_homepage(base_url, product_index=1)

        result = page.click_add_to_cart_and_wait_swal()

        assert result, \
            "TC-2 FAIL: Đã đăng nhập nhưng không thêm được vào giỏ hàng."
# ==========================================================
# HELPERS
# ==========================================================

def navigate_to_product(page: AddToCartPage, keyword: str):

    page.navigate_by_search(base_url, keyword)
    if not page.is_on_product_detail_page():
        pytest.skip(
            f"Không điều hướng được đến trang chi tiết SP '{keyword}'. "
            f"URL hiện tại: {page.get_current_url()}"
        )


def find_size_option_text(page: AddToCartPage, size_contains: str) -> str | None:

    for opt in page.get_size_options():
        if size_contains.upper() in opt.upper():
            return opt
    return None


# ==========================================================
# NHÓM: BIZ ADD TO CART – 
# ==========================================================

class TestAddToCart:

    def test_tc7_add_to_cart_success(self, logged_in_driver):
       
        page = AddToCartPage(logged_in_driver)
        navigate_to_product(page, PRODUCT_ADD_TO_CART_SUCCESS["keyword"])

        swal_appeared = page.click_add_to_cart_and_wait_swal(timeout=SWAL_APPEAR_TIMEOUT)

        assert swal_appeared, (
            "TC-7 FAIL: Sau khi click 'Thêm vào giỏ', "
            "phải xuất hiện SweetAlert thông báo thành công."
        )

        swal_title = page.get_swal_title().lower()
        swal_text  = page.get_swal_text().lower()

        assert any(
            kw in swal_title
            for kw in PRODUCT_ADD_TO_CART_SUCCESS["expected_swal_title_keywords"]
        ), (
            f"TC-7 FAIL: Title SweetAlert phải chứa 'thành công'. "
            f"Title thực tế: '{page.get_swal_title()}'"
        )
        assert any(
            kw in swal_text
            for kw in PRODUCT_ADD_TO_CART_SUCCESS["expected_swal_text_keywords"]
        ), (
            f"TC-7 FAIL: Text SweetAlert phải chứa thông tin giỏ hàng. "
            f"Text thực tế: '{page.get_swal_text()}'"
        )

        swal_disappeared = page.wait_for_swal_disappear(timeout=SWAL_DISAPPEAR_TIMEOUT)
        assert swal_disappeared, \
            "TC-7 FAIL: SweetAlert phải TỰ BIẾN MẤT sau vài giây (không cần click)."

    def test_tc8_add_to_cart_out_of_stock(self, logged_in_driver):
       
        page = AddToCartPage(logged_in_driver)
        navigate_to_product(page, PRODUCT_ADD_TO_CART_OUT_OF_STOCK["keyword"])

        assert page.is_product_name_visible(), \
            "TC-8 FAIL: Tên SP không hiển thị."
        assert page.is_product_image_displayed(), \
            "TC-8 FAIL: Ảnh SP không hiển thị."

        assert page.is_add_to_cart_btn_disabled(), (
            "TC-8 FAIL: Nút Thêm Vào Giỏ phải DISABLED ngay khi vào trang SP hết hàng. "
            f"Text nút: '{page.get_add_to_cart_btn_text()}'"
        )

        swal_appeared = page.wait_for_swal_appear(timeout=SWAL_APPEAR_TIMEOUT)
        assert swal_appeared, \
            "TC-8 FAIL: Phải xuất hiện SweetAlert khi vào SP hết hàng."

        swal_title = page.get_swal_title().lower()
        assert any(
            kw in swal_title
            for kw in PRODUCT_ADD_TO_CART_OUT_OF_STOCK["expected_swal_title_keywords"]
        ), (
            f"TC-8 FAIL: SweetAlert title phải chứa từ khóa hết hàng. "
            f"Title: '{page.get_swal_title()}'"
        )

        swal_text = page.get_swal_text().lower()
        assert any(
            kw in swal_text
            for kw in PRODUCT_ADD_TO_CART_OUT_OF_STOCK["expected_swal_text_keywords"]
        ), (
            f"TC-8 FAIL: SweetAlert text không đúng. "
            f"Text: '{page.get_swal_text()}'"
        )

        page.wait_for_swal_disappear(timeout=SWAL_DISAPPEAR_TIMEOUT)

    def test_tc9_add_to_cart_out_of_size(self, logged_in_driver):
       
        page = AddToCartPage(logged_in_driver)
        navigate_to_product(page, PRODUCT_ADD_TO_CART_OUT_OF_SIZE["keyword"])

        assert page.is_size_dropdown_visible(), \
            "TC-9 FAIL: Dropdown Size không hiển thị."

        out_size_text = find_size_option_text(
            page, PRODUCT_ADD_TO_CART_OUT_OF_SIZE["out_of_size_contains"]
        )
        if out_size_text is None:
            pytest.skip(
                f"TC-9: Size '{PRODUCT_ADD_TO_CART_OUT_OF_SIZE['out_of_size_contains']}' "
                f"không có trong dropdown. Các size: {page.get_size_options()}."
            )

        page.select_size(size_text=out_size_text)
        page.wait_for_btn_text_update(timeout=3)

        swal_appeared = page.wait_for_swal_appear(timeout=SWAL_APPEAR_TIMEOUT)
        assert swal_appeared, (
            f"TC-9 FAIL: Sau khi chọn size '{out_size_text}' đã hết, "
            "phải xuất hiện SweetAlert 'Số lượng hàng trong kho không đủ'."
        )

        combined = page.get_swal_text().lower() + " " + page.get_swal_title().lower()
        assert any(
            kw in combined
            for kw in PRODUCT_ADD_TO_CART_OUT_OF_SIZE["expected_swal_text_keywords"]
        ), (
            f"TC-9 FAIL: SweetAlert phải chứa thông báo không đủ hàng. "
            f"Title: '{page.get_swal_title()}' | Text: '{page.get_swal_text()}'"
        )

        assert page.is_add_to_cart_btn_disabled(), (
            f"TC-9 FAIL: Nút phải DISABLED sau khi chọn size '{out_size_text}' đã hết."
        )

        available_size = find_size_option_text(
            page, PRODUCT_ADD_TO_CART_OUT_OF_SIZE.get("available_size", "M")
        )
        if available_size:
            page.close_swal_if_visible()
            page.select_size(size_text=available_size)
            page.wait_for_btn_text_update(timeout=3)
            assert page.is_add_to_cart_btn_enabled(), (
                f"TC-9 FAIL: Với size '{available_size}' còn hàng, nút phải ENABLED. "
                f"Text nút: '{page.get_add_to_cart_btn_text()}'"
            )

    def test_tc10_add_to_cart_exceed_quantity(self, logged_in_driver):
        
        page = AddToCartPage(logged_in_driver)
        navigate_to_product(page, PRODUCT_EXCEED_QUANTITY["keyword"])

        page.set_quantity(PRODUCT_EXCEED_QUANTITY["exceed_qty"])

        try:
            page.click_add_to_cart()
        except Exception:
            pass

        swal_appeared = page.wait_for_swal_appear(timeout=SWAL_APPEAR_TIMEOUT)
        assert swal_appeared, (
            f"TC-10 FAIL: Nhập SL={PRODUCT_EXCEED_QUANTITY['exceed_qty']} > tồn kho, "
            "phải xuất hiện SweetAlert cảnh báo."
        )

        combined = page.get_swal_text().lower() + " " + page.get_swal_title().lower()
        assert any(
            kw in combined
            for kw in PRODUCT_EXCEED_QUANTITY["expected_swal_text_keywords"]
        ), (
            "TC-10 FAIL: SweetAlert phải chứa thông báo không đủ hàng. "
            f"Title: '{page.get_swal_title()}' | Text: '{page.get_swal_text()}'"
        )


