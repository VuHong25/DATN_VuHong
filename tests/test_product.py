
import pytest
from selenium.webdriver.common.by import By

from pages.product_page import ProductDetailPage
from conftest import base_url, LOGIN_PASSWORD, LOGIN_USERNAME
from data.test_data_product import (
   
    PRODUCT_IN_STOCK,
    PRODUCT_OUT_OF_STOCK,
    PRODUCT_OUT_OF_SIZE, 
    PRODUCT_OUT_OF_STOCK,
    PRODUCT_OUT_OF_SIZE,
    PRODUCT_WITH_REVIEW,
    PRODUCT_NO_REVIEW,
    
    SWAL_APPEAR_TIMEOUT,
    SWAL_DISAPPEAR_TIMEOUT,
)


# ==========================================================
# HELPERS
# ==========================================================

def navigate_to_product(page: ProductDetailPage, keyword: str):
   
    page.navigate_by_search(base_url, keyword)
    if not page.is_on_product_detail_page():
        pytest.skip(
            f"Không điều hướng được đến trang chi tiết SP '{keyword}'. "
            f"URL hiện tại: {page.get_current_url()}"
        )


def find_size_option_text(page: ProductDetailPage, size_contains: str) -> str | None:

    options = page.get_size_options()
    for opt in options:
        if size_contains.upper() in opt.upper():
            return opt
    return None


# ==========================================================
# NHÓM 1: ACCESS RIGHT – TC-1, TC-2
# ==========================================================

class TestProductDetailAccessRight:


    def test_tc01_view_product_not_logged_in(self, driver):
        """TC-1: Chưa đăng nhập → vẫn xem được chi tiết SP."""
        page = ProductDetailPage(driver)
        page.navigate_by_click_on_homepage(base_url, product_index=1)

        assert page.is_on_product_detail_page(), (
            "TC-1 FAIL: Chưa đăng nhập nhưng không xem được chi tiết SP. "
            f"URL: {page.get_current_url()}"
        )
        assert page.is_product_name_visible(), \
            "TC-1 FAIL: Tên SP không hiển thị khi chưa đăng nhập."

    def test_tc02_view_product_logged_in(self, logged_in_driver):
        """TC-2: Đã đăng nhập → vẫn xem được chi tiết SP."""
        page = ProductDetailPage(logged_in_driver)
        page.navigate_by_click_on_homepage(base_url, product_index=1)

        assert page.is_on_product_detail_page(), (
            "TC-2 FAIL: Đã đăng nhập nhưng không xem được chi tiết SP. "
            f"URL: {page.get_current_url()}"
        )
        assert page.is_product_name_visible(), \
            "TC-2 FAIL: Tên SP không hiển thị khi đã đăng nhập."



# ==========================================================
# NHÓM 3: BIZ VIEW – TC-7, TC-8, TC-9, TC-11, TC-12
# ==========================================================

class TestProductDetailBizView:
    
    def test_tc07_view_in_stock_product(self, driver):
        
        page = ProductDetailPage(driver)
        navigate_to_product(page, PRODUCT_IN_STOCK["keyword"])

        assert page.is_product_name_visible(),  "TC-7 FAIL: Tên SP không hiển thị."
        assert page.is_product_image_displayed(), "TC-7 FAIL: Ảnh SP không hiển thị."
        assert page.is_size_dropdown_visible(), "TC-7 FAIL: Dropdown Size không hiển thị."
        assert page.is_add_to_cart_btn_enabled(), (
            "TC-7 FAIL: Nút Thêm Vào Giỏ phải ENABLED với SP còn hàng. "
            f"Text: '{page.get_add_to_cart_btn_text()}'"
        )

    def test_tc08_view_out_of_stock_product(self, driver):
       
        page = ProductDetailPage(driver)
        navigate_to_product(page, PRODUCT_OUT_OF_STOCK["keyword"])

        # Kiểm tra thông tin cơ bản vẫn hiển thị
        assert page.is_product_name_visible(),  "TC-8 FAIL: Tên SP không hiển thị."
        # assert page.is_product_price_visible(), "TC-8 FAIL: Giá SP không hiển thị."
        assert page.is_product_image_displayed(), "TC-8 FAIL: Ảnh SP không hiển thị."

        assert page.is_add_to_cart_btn_disabled(), (
            "TC-8 FAIL: Nút Thêm Vào Giỏ phải DISABLED với SP hết hàng. "
            f"Text nút: '{page.get_add_to_cart_btn_text()}'"
        )

        swal_appeared = page.wait_for_swal_appear(timeout=SWAL_APPEAR_TIMEOUT)
        assert swal_appeared, (
        "TC-8 FAIL: Phải xuất hiện SweetAlert khi vào SP hết hàng."
    )
        swal_title = page.get_swal_title().lower()
        assert any(
            kw in swal_title
            for kw in PRODUCT_OUT_OF_STOCK["expected_swal_title_keywords"]
        ), (
            f"TC-8 FAIL: SweetAlert title phải chứa từ khóa thất bại. "
            f"Title thực tế: '{page.get_swal_title()}'"
        )
        swal_text = page.get_swal_text().lower()
        assert any(
            kw.lower() in swal_text
            for kw in PRODUCT_OUT_OF_STOCK["expected_swal_text_keywords"]
        ), (
            "TC-8 FAIL: Nội dung popup sai. "
            f"Actual: '{page.get_swal_text()}'"
        )
        page.wait_for_swal_disappear(timeout=SWAL_DISAPPEAR_TIMEOUT)

    def test_tc09_view_out_of_size_product(self, driver):
     
        page = ProductDetailPage(driver)
        navigate_to_product(page, PRODUCT_OUT_OF_SIZE["keyword"])

        # Kiểm tra thông tin cơ bản
        assert page.is_product_name_visible(),  "TC-9 FAIL: Tên SP không hiển thị."
        assert page.is_product_image_displayed(), "TC-9 FAIL: Ảnh SP không hiển thị."
        assert page.is_size_dropdown_visible(), "TC-9 FAIL: Dropdown Size không hiển thị."

        out_size_text = find_size_option_text(
            page, PRODUCT_OUT_OF_SIZE["out_of_size_contains"]
        )
        if out_size_text is None:
            pytest.skip(
                f"TC-9: Size chứa '{PRODUCT_OUT_OF_SIZE['out_of_size_contains']}' "
                f"không có trong dropdown. Các size: {page.get_size_options()}. "
                "Kiểm tra lại DB hoặc text option trong test_data."
            )

        page.select_size(size_text=out_size_text)
        page.wait_for_btn_text_update(timeout=3)

        swal_appeared = page.wait_for_swal_appear(timeout=SWAL_APPEAR_TIMEOUT)
        assert swal_appeared, (
            f"TC-9 FAIL: Sau khi chọn size '{out_size_text}' đã hết, "
            "phải xuất hiện SweetAlert thông báo."
        )

        swal_text = page.get_swal_text().lower()
        swal_title = page.get_swal_title().lower()
        combined = swal_text + " " + swal_title

        assert any(
            kw in combined
            for kw in PRODUCT_OUT_OF_SIZE["expected_swal_text_keywords"]
        ), (
            f"TC-9 FAIL: SweetAlert phải chứa thông báo không đủ hàng. "
            f"Title: '{page.get_swal_title()}' | Text: '{page.get_swal_text()}'"
        )

        assert page.is_add_to_cart_btn_disabled(), (
            f"TC-9 FAIL: Nút phải DISABLED sau khi chọn size '{out_size_text}' đã hết."
        )

    def test_tc10_product_with_review(self, driver):
        page = ProductDetailPage(driver)
        navigate_to_product(page, PRODUCT_WITH_REVIEW["keyword"])

        page.scroll_to_review_section()
        review_text = page.get_review_section_text()

        assert review_text != "", (
            "TC-10 FAIL: Section đánh giá phải hiển thị nội dung khi SP có đánh giá. "
            "Kiểm tra SP 'Áo sơ mi nam trơn' có đánh giá trong DB chưa."
        )
        assert "Chưa có đánh giá nào" not in review_text, (
            "TC-10 FAIL: SP có đánh giá không được hiển thị 'Chưa có đánh giá nào'."
        )

    def test_tc11_product_no_review(self, driver):
        
        page = ProductDetailPage(driver)
        navigate_to_product(page, PRODUCT_NO_REVIEW["keyword"])

        page.scroll_to_review_section()

        assert page.is_no_review_message_visible(), (
            f"TC-11 FAIL: Phải hiển thị text tĩnh "
            f"'{PRODUCT_NO_REVIEW['expected_no_review_text']}' "
            "trong section đánh giá (KHÔNG phải popup). "
            f"Text section: '{page.get_review_section_text()[:100]}'"
        )
       
        assert not page.is_swal_visible(), \
            "TC-11 FAIL: 'Chưa có đánh giá nào' phải là text tĩnh, KHÔNG phải popup SweetAlert."


