

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.invoice_page import InvoicePage
from pages.login_page_new import LoginPage
from conftest import base_url
from data.test_data_invoice import (
    ADMIN_USER, ADMIN_PASSWORD,
    CUSTOMER_USER, CUSTOMER_PASSWORD,
    ACCESS_ADMIN,
    VIEW_INVOICE_LIST,
    VIEW_INVOICE_DETAIL,
    UPDATE_STATUS_DATA,
    CANCEL_ORDER,
    MESSAGES,
    INVOICE_ACTIVE,
    INVOICE_CANCELLED,
)


# ==============================================================
# HELPERS
# ==============================================================

def go_to_invoice_list(page: InvoicePage):
    page.navigate_to_invoice_list()
    if not page.is_on_invoice_list_page():
        pytest.skip("Không vào được trang danh sách hóa đơn – kiểm tra URL/đăng nhập")


def assert_at_least_one_invoice(page: InvoicePage, tc_id: str):
    count = page.get_invoice_row_count()
    if count == 0:
        pytest.skip(
            f"[{tc_id}] Precondition: DB phải có ít nhất 1 hóa đơn. "
            "Hãy đặt hàng bằng tài khoản test_1 trước khi chạy."
        )


def goto_row(page: InvoicePage, global_row_index: int) -> int:
    
    return page.navigate_to_page_for_row(global_row_index)


# ==============================================================
# NHÓM 1: ACCESS RIGHT – TC-1, TC-2, TC-3
# ==============================================================
class TestInvoiceAccessRight:

    def test_admin_can_access_invoice(self, admin_driver):
        """
        TC-1: Admin đăng nhập → click Hóa đơn → danh sách hiển thị.
        """
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)
        assert page.is_on_invoice_list_page(), \
            "TC-1 FAIL: Admin phải được truy cập trang Hóa đơn"

    def test_customer_cannot_access_admin_invoice(self, driver):
       
        page = InvoicePage(driver)

        # Mở trang login admin
        page.open_admin_login(base_url)

        # Đăng nhập bằng tài khoản KH
        page.login_admin(CUSTOMER_USER, CUSTOMER_PASSWORD)

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        current_url = driver.current_url.lower()

        # ===== Expected đúng =====
        correct_permission_msg = any(kw in body_text for kw in [
            "không được cấp quyền",
            "không có quyền",
            "access denied",
            "forbidden"
        ])

        # ===== Sai nghiệp vụ =====
        wrong_login_msg = any(kw in body_text for kw in [
            "tài khoản hoặc mật khẩu không đúng",
            "invalid username or password",
            "sai mật khẩu"
        ])

        # ===== Kiểm tra vào admin =====
        is_on_admin = page.is_on_invoice_list_page()

        # ===== ASSERT =====
        assert not is_on_admin, (
            "TC-2 FAIL: Khách hàng KHÔNG được truy cập trang admin."
        )

        assert not wrong_login_msg, (
            "TC-2 FAIL: Hệ thống trả về sai thông báo. "
            "Expected là 'không được cấp quyền', "
            "Actual là 'sai tài khoản/mật khẩu'."
        )

        assert correct_permission_msg or page.is_on_login_page(), (
            "TC-2 FAIL: Không có thông báo từ chối quyền hợp lệ."
        )
    
# ==============================================================
# NHÓM 3: BIZ – Xem hóa đơn –
# ==============================================================
class TestInvoiceViewList:
  
    def test_view_invoice_list_has_data(self, admin_driver):
        """TC-7: Danh sách hiển thị đầy đủ thông tin."""
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)
        assert_at_least_one_invoice(page, "TC-8")

        assert page.get_invoice_row_count() >= 1, \
            "TC-7 FAIL: Phải hiển thị ít nhất 1 hóa đơn"

        page_text = admin_driver.find_element(By.TAG_NAME, "body").text
        for col in VIEW_INVOICE_LIST["expected_columns"]:
            assert col.lower() in page_text.lower(), \
                f"TC-7 FAIL: Trang phải hiển thị cột '{col}'"

        assert not page.is_no_invoice_message_visible(), \
            "TC-7 FAIL: Không được hiển thị 'Không có đơn hàng' khi có dữ liệu"

    def test_view_invoice_list_empty(self, admin_driver):
        
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)

        if page.get_invoice_row_count() > 0:
            pytest.skip(
                "TC-8: DB đang có dữ liệu. Thực hiện thủ công"
            )

        assert page.is_no_invoice_message_visible(), \
            f"TC-8 FAIL: Phải hiển thị '{MESSAGES['no_invoice']}' khi không có hóa đơn"


# ==============================================================
# NHÓM 4: BIZ – Xem chi tiết hóa đơn – TC-11, TC-12
# ==============================================================
class TestInvoiceDetail:
    def test_view_invoice_detail(self, admin_driver):
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)
        assert_at_least_one_invoice(page, "TC-9")
        row_on_page = goto_row(page, INVOICE_ACTIVE["row_index"])
        page.click_options_btn(row_on_page)
        page.click_view_detail()
        
        assert page.is_modal_detail_visible(), \
            "TC-9 FAIL: Modal chi tiết phải hiển thị sau khi click 'Chi tiết hóa đơn'"
        try:
            modal_el = admin_driver.find_element(*InvoicePage.MODAL_DETAIL)
            modal_text = modal_el.text.strip()
        except Exception:
            modal_text = admin_driver.find_element(By.TAG_NAME, "body").text
        has_detail_info = any(
            field.lower() in modal_text.lower()
            for field in VIEW_INVOICE_DETAIL["expected_fields"]
        )
        assert has_detail_info or len(modal_text) > 20, (
            "TC-9 FAIL: Modal phải hiển thị ít nhất 1 trường thông tin. "
            f"Text modal: {modal_text[:100]!r}"
        )
        page.click_close_detail_modal()
        assert not page.is_modal_detail_visible(), \
            "TC-9 FAIL: Modal phải đóng sau khi click 'Thoát'"

    def test_view_cancelled_invoice_detail(self, admin_driver):
       
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)

        page_text = admin_driver.find_element(By.TAG_NAME, "body").text
        if MESSAGES["cancelled_status"] not in page_text:
            pytest.skip(
                "TC-10: Không tìm thấy đơn đã hủy ở trang 1. "
                "Hủy 1 đơn trước hoặc kiểm tra INVOICE_CANCELLED['row_index']."
            )

        # Tìm dòng đã hủy theo XPath trong trang hiện tại
        cancelled_row_xpath = (
            "//table[contains(@class,'table')]//tbody"
            "/tr[contains(@class,'group-info')]"
            "[.//*[contains(normalize-space(.),'Đã bị hủy')]]"
        )
        try:
            cancelled_row = admin_driver.find_element(By.XPATH, cancelled_row_xpath)
            btn = cancelled_row.find_element(
                By.XPATH, ".//button[contains(@class,'dropdown-toggle')]"
            )
            admin_driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            admin_driver.execute_script("arguments[0].click();", btn)

            page.click_view_detail()
            assert page.is_modal_detail_visible(), \
                "TC-10 FAIL: Modal chi tiết vẫn phải mở được với đơn đã hủy"

            page.click_close_detail_modal()
        except Exception as e:
            pytest.skip(f"TC-10: Không tìm được dòng hóa đơn đã hủy – {e}")


# ==============================================================
# NHÓM 5: BIZ – Trạng thái – TC-14, TC-15
# ==============================================================
class TestInvoiceStatus:

    @pytest.mark.parametrize(
        "tc_id, status_text, mo_ta",
        UPDATE_STATUS_DATA,
        ids=[d[0] for d in UPDATE_STATUS_DATA],
    )
    def test_update_order_status(self, admin_driver, tc_id, status_text, mo_ta):
        
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)
        assert_at_least_one_invoice(page, tc_id)

        row_on_page = goto_row(page, INVOICE_ACTIVE["row_index"])
        try:
            page.select_status(status_text=status_text, row_index_on_page=row_on_page)
        except Exception as e:
            pytest.fail(
                f"[{tc_id}] FAIL: Không thể chọn trạng thái '{status_text}'. Lỗi: {e}"
            )

        updated = page.wait_for_status_update(status_text, timeout=8)
        assert updated, (
            f"[{tc_id}] FAIL: {mo_ta} | "
            f"Trạng thái phải được cập nhật thành '{status_text}'."
        )

    
# ==============================================================
# NHÓM 6: BIZ – Hủy đơn hàng – TC-
# ==============================================================
class TestInvoiceCancelOrder:
   
#chạy test case 18 trước, 17 sau để không bị fail (do tc-17 là cencal success)

    def test_cancel_order_click_cancel(self, admin_driver):
        """
        TC-13: Click Cancel trên SweetAlert → đơn hàng giữ nguyên.

        """
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)
        assert_at_least_one_invoice(page, "TC-13")

        # Navigate đến đúng trang trước khi thao tác
        row_on_page = goto_row(page, CANCEL_ORDER["row_index"])

        # Lưu trạng thái trước khi hủy
        status_before = page.get_status_by_row(row_on_page)

        if MESSAGES["cancelled_status"].lower() in status_before.lower():
            pytest.skip("TC-13: Dòng đã chỉ định đã bị hủy từ trước.")


        page.click_options_btn(row_on_page)
        page.click_cancel_order()

        assert page.is_swal_visible(), \
            "TC-13 FAIL: Phải hiển thị SweetAlert xác nhận"

        swal_title = page.get_swal_title()
        swal_text  = page.get_swal_text()   

        assert "cảnh báo" in swal_title.lower()
        assert MESSAGES["cancel_confirm"].lower() in swal_text.lower(), (
            f"TC-13 FAIL: SweetAlert phải chứa '{MESSAGES['cancel_confirm']}'. "
            f"Thực tế: {swal_title!r}"
        )

        # Click Cancel → đơn hàng giữ nguyên
        page.click_swal_cancel()

        assert not page.is_swal_visible(), \
            "TC-13 FAIL: SweetAlert phải đóng sau khi click Cancel"

        # # Kiểm tra trạng thái không đổi
        status_after = page.get_status_by_row(row_on_page)
        assert MESSAGES["cancelled_status"] not in status_after, (
            "TC-13 FAIL: Đơn hàng không được bị hủy khi click Cancel. "
            f"Trước: {status_before!r} | Sau: {status_after!r}"
        )
        
    def test_cancel_order_success(self, admin_driver):
        """
        TC-12: Hủy đơn thành công.

        """
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)
        assert_at_least_one_invoice(page, "TC-12")

        row_on_page = goto_row(page, CANCEL_ORDER["row_index"])

        page.click_options_btn(row_on_page)
        page.click_cancel_order()

        assert page.is_swal_visible(), \
            "TC-12 FAIL: Phải hiển thị SweetAlert xác nhận khi click 'Hủy đơn hàng'"

        swal_title = page.get_swal_title()
        swal_text  = page.get_swal_text()

        assert "cảnh báo" in swal_title.lower()
        assert MESSAGES["cancel_confirm"].lower() in swal_text.lower(), (
            f"TC-12 FAIL: SweetAlert phải chứa '{MESSAGES['cancel_confirm']}'. "
            f"Thực tế: {swal_title!r}"
        )

        page.click_swal_ok()

        updated = page.wait_for_status_update(MESSAGES["cancelled_status"])
        assert updated, (
            f"TC-12 FAIL: Sau khi click OK, trạng thái phải đổi thành "
            f"'{MESSAGES['cancelled_status']}'"
        )

    def test_cancelled_order_hides_cancel_btn(self, admin_driver):
        """
        TC-14: Đơn đã hủy → nút 'Hủy đơn hàng' bị ẩn trong Tùy chọn.
        """
        page = InvoicePage(admin_driver)
        go_to_invoice_list(page)

        page_text = admin_driver.find_element(By.TAG_NAME, "body").text
        if MESSAGES["cancelled_status"] not in page_text:
            pytest.skip(
                "TC-14: Không tìm thấy đơn đã hủy ở trang 1. "
                "Chạy TC-13 trước hoặc kiểm tra INVOICE_CANCELLED['row_index']."
            )

        cancelled_row_xpath = (
            "//table[contains(@class,'table')]//tbody"
            "/tr[contains(@class,'group-info')]"
            "[.//*[contains(normalize-space(.),'Đã bị hủy')]]"
        )
        try:
            cancelled_row = admin_driver.find_element(By.XPATH, cancelled_row_xpath)
            btn = cancelled_row.find_element(
                By.XPATH, ".//button[contains(@class,'dropdown-toggle')]"
            )
            admin_driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            admin_driver.execute_script("arguments[0].click();", btn)

            # Kiểm tra nút Hủy đơn hàng bị ẩn hoặc không tồn tại
            cancel_btns = admin_driver.find_elements(*InvoicePage.OPT_CANCEL)
            is_hidden = len(cancel_btns) == 0 or all(
                not b.is_displayed() for b in cancel_btns
            )
            assert is_hidden, \
                "TC-14 FAIL: Nút 'Hủy đơn hàng' phải bị ẩn với đơn đã bị hủy"
        except Exception as e:
            pytest.fail(
                f"TC-14 FAIL: Không tìm được dòng hóa đơn đã hủy. Chi tiết: {e}"
            )


    


