
import pytest
from conftest import base_url
from pages.register_page import RegisterPage
from data.test_data_register import (
    HO_TEN_CASES, SDT_CASES, EMAIL_CASES,
    MAT_KHAU_CASES, XAC_NHAN_MK_CASES, TAI_KHOAN_CASES,
    DIA_CHI_CASES, NGAY_SINH_CASES,
    VALID_HO_TEN, VALID_SDT, VALID_DIA_CHI, VALID_GIOI_TINH,
    VALID_NGAY_SINH, VALID_MAT_KHAU,
    make_valid_email, make_valid_username,
    MSG_DUPLICATE_USERNAME, MSG_DUPLICATE_EMAIL,
)


# ===========================================================================
# HELPER – dùng chung trong nhiều test
# ===========================================================================

def open_register(driver) -> RegisterPage:
    """Khởi tạo RegisterPage và điều hướng đến form đăng ký."""
    page = RegisterPage(driver)
    page.open_register_page(base_url)
    return page


def fill_valid_form_except(page: RegisterPage, **overrides):
  
    defaults = dict(
        ho_ten    = VALID_HO_TEN,
        sdt       = VALID_SDT,
        dia_chi   = VALID_DIA_CHI,
        gioi_tinh = VALID_GIOI_TINH,
        email     = make_valid_email(),
        ngay_sinh = VALID_NGAY_SINH,
        tai_khoan = make_valid_username(),
        mat_khau  = VALID_MAT_KHAU,
        xac_nhan_mk = VALID_MAT_KHAU,
    )
    defaults.update(overrides)
    page.fill_form(**defaults)


# ===========================================================================
# TC-01: ACCESS RIGHT – Chưa đăng nhập, truy cập trang đăng ký
# ===========================================================================

class TestAccessRight:

    def test_TC01_mo_trang_dang_ky_chua_dang_nhap(self, driver):
       
        page = open_register(driver)
        # Kiểm tra ít nhất input họ tên xuất hiện → form đã load
        assert page.check_visible(RegisterPage.INPUT_HO_TEN), \
            "Form đăng ký không hiển thị khi chưa đăng nhập"

    def test_TC02_da_dang_nhap_khong_hien_nut_dang_ky(self, logged_in_driver):
        
        page = RegisterPage(logged_in_driver)
        page.open(base_url)
        # Khi đã đăng nhập, link Đăng ký không được xuất hiện
        assert not page.check_visible(RegisterPage.DROPDOWN_DANG_KY), \
            "Đã đăng nhập nhưng vẫn hiển thị link Đăng ký"


# ===========================================================================
# TC-10 → 18: VALIDATION HỌ TÊN
# ===========================================================================
class TestValidationHoTen:
    @pytest.mark.parametrize(
        "test_id, ho_ten, expected_msg, error_type, description",
        HO_TEN_CASES,
        ids=[c[0] for c in HO_TEN_CASES]
    )

    def test_ho_ten(self, driver, test_id, ho_ten,
                    expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(page, ho_ten=ho_ten)
        page.scroll_to_submit_button()
        
        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_HO_TEN), \
                f"[{test_id}] Kỳ vọng HTML5 đánh dấu invalid: {description}"
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower(), \
                f"[{test_id}] Trang đã redirect dù form chưa hợp lệ: {description}"
            
        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', got '{error_text}' – {description}"
            
        else:  
            assert not page.is_field_invalid_html5(RegisterPage.INPUT_HO_TEN), \
                f"[{test_id}] Kỳ vọng HTML5 KHÔNG đánh dấu invalid: {description}"


# ===========================================================================
# TC-20 → 26: VALIDATION SỐ ĐIỆN THOẠI
# ===========================================================================

class TestValidationSoDienThoai:

    @pytest.mark.parametrize(
        "test_id, sdt, expected_msg, error_type, description",
        SDT_CASES,
        ids=[c[0] for c in SDT_CASES]
    )
    def test_so_dien_thoai(self, driver, test_id, sdt,
                           expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(page, sdt=sdt)
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_SDT), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', got '{error_text}'"

        else:
            assert not page.is_field_invalid_html5(RegisterPage.INPUT_SDT), \
                f"[{test_id}] Kỳ vọng không có HTML5 error: {description}"


# ===========================================================================
# TC-27 → 31: VALIDATION EMAIL
# ===========================================================================

class TestValidationEmail:

    @pytest.mark.parametrize(
        "test_id, email, expected_msg, error_type, description",
        EMAIL_CASES,
        ids=[c[0] for c in EMAIL_CASES]
    )
    def test_email_invalid(self, driver, test_id, email,
                           expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(page, email=email)
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_EMAIL), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', actual '{error_text}'"

    def test_TC31_email_hop_le(self, driver):
        """
        Email hợp lệ → hệ thống cho phép tiếp tục (không có lỗi email).
        Dùng random để tránh trùng lặp email.
        """
        page = open_register(driver)
        unique_email = make_valid_email()
        fill_valid_form_except(page, email=unique_email)
        page.scroll_to_submit_button()

        # Không có HTML5 error trên trường email
        assert not page.is_field_invalid_html5(RegisterPage.INPUT_EMAIL), \
            "TC-31: Email hợp lệ nhưng bị HTML5 đánh dấu invalid"


# ===========================================================================
# TC-33 → 35: VALIDATION MẬT KHẨU
# ===========================================================================

class TestValidationMatKhau:

    @pytest.mark.parametrize(
        "test_id, mat_khau, expected_msg, error_type, description",
        MAT_KHAU_CASES,
        ids=[c[0] for c in MAT_KHAU_CASES]
    )
    def test_mat_khau(self, driver, test_id, mat_khau,
                      expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(
            page,
            mat_khau=mat_khau,
            xac_nhan_mk=mat_khau   # khớp để tránh lỗi xác nhận
        )
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_MAT_KHAU), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', got '{error_text}'"

        else:
            assert not page.is_field_invalid_html5(RegisterPage.INPUT_MAT_KHAU), \
                f"[{test_id}] Không kỳ vọng HTML5 error: {description}"


# ===========================================================================
# TC-36 → 38: VALIDATION XÁC NHẬN MẬT KHẨU
# ===========================================================================

class TestValidationXacNhanMatKhau:

    @pytest.mark.parametrize(
        "test_id, mat_khau, xac_nhan_mk, expected_msg, error_type, description",
        XAC_NHAN_MK_CASES,
        ids=[c[0] for c in XAC_NHAN_MK_CASES]
    )
    def test_xac_nhan_mat_khau(self, driver, test_id, mat_khau, xac_nhan_mk,
                                expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(
            page,
            mat_khau=mat_khau,
            xac_nhan_mk=xac_nhan_mk
        )
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_XAC_NHAN_MK), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', got '{error_text}'"


# ===========================================================================
# TC-39 → 47: VALIDATION TÀI KHOẢN
# ===========================================================================

class TestValidationTaiKhoan:

    @pytest.mark.parametrize(
        "test_id, tai_khoan, expected_msg, error_type, description",
        TAI_KHOAN_CASES,
        ids=[c[0] for c in TAI_KHOAN_CASES]
    )
    def test_tai_khoan(self, driver, test_id, tai_khoan,
                       expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(page, tai_khoan=tai_khoan)
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_TAI_KHOAN), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', actual '{error_text}'"

        else:
            assert not page.is_field_invalid_html5(RegisterPage.INPUT_TAI_KHOAN), \
                f"[{test_id}] Không kỳ vọng HTML5 error: {description}"


# ===========================================================================
# TC-48 → 55: VALIDATION ĐỊA CHỈ
# ===========================================================================

class TestValidationDiaChi:

    @pytest.mark.parametrize(
        "test_id, dia_chi, expected_msg, error_type, description",
        DIA_CHI_CASES,
        ids=[c[0] for c in DIA_CHI_CASES]
    )
    def test_dia_chi(self, driver, test_id, dia_chi,
                     expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(page, dia_chi=dia_chi)
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_DIA_CHI), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', got '{error_text}'"

        else:
            assert not page.is_field_invalid_html5(RegisterPage.INPUT_DIA_CHI), \
                f"[{test_id}] Không kỳ vọng HTML5 error: {description}"


# ===========================================================================
# TC-56 → 58: VALIDATION NGÀY SINH
# ===========================================================================

class TestValidationNgaySinh:

    @pytest.mark.parametrize(
        "test_id, ngay_sinh, expected_msg, error_type, description",
        NGAY_SINH_CASES,
        ids=[c[0] for c in NGAY_SINH_CASES]
    )
    def test_ngay_sinh(self, driver, test_id, ngay_sinh,
                       expected_msg, error_type, description):
        page = open_register(driver)
        fill_valid_form_except(page, ngay_sinh=ngay_sinh)
        page.scroll_to_submit_button()

        if error_type == "html5":
            page.click_dang_ky()
            assert page.is_field_invalid_html5(RegisterPage.INPUT_NGAY_SINH), \
                f"[{test_id}] HTML5 phải invalid: {description}"
            
            assert "signup" in page.get_current_url().lower() \
                   or "dang-ky" in page.get_current_url().lower()

        elif error_type == "span":
            page.click_dang_ky()
            error_text = page.get_span_error_text()
            assert expected_msg in error_text, \
                f"[{test_id}] Expected '{expected_msg}', got '{error_text}'"

        else:
            assert not page.is_field_invalid_html5(RegisterPage.INPUT_NGAY_SINH), \
                f"[{test_id}] Không kỳ vọng HTML5 error: {description}"


# ===========================================================================
# TC-59 → 62: BUSINESS LOGIC
# ===========================================================================

class TestBusinessLogic:

    def test_TC59_dang_ky_thanh_cong(self, driver):
        
        page = open_register(driver)
        page.fill_form(
            ho_ten      = "Vũ Thị Hồng",
            sdt         = "0123456789",
            dia_chi     = "Bắc Ninh",
            gioi_tinh   = "nu",
            email       = make_valid_email(),       # random unique
            ngay_sinh   = VALID_NGAY_SINH,
            tai_khoan   = make_valid_username(),    # random unique
            mat_khau    = "123456",
            xac_nhan_mk = "123456",
        )
        page.scroll_to_submit_button()
        page.click_dang_ky()

        # Chờ redirect về trang chủ
        redirected = page.wait_for_home_page(timeout=20)
        assert redirected, \
            f"TC-59: Đăng ký thành công nhưng không redirect. URL: {page.get_current_url()}"

        assert not page.get_span_error_text(timeout=3), \
            "TC-59: Không nên hiển thị thông báo sau khi đăng ký thành công"

    def test_TC60_dang_ky_tai_khoan_da_ton_tai(self, driver):
       
        page = open_register(driver)
        page.fill_form(
            ho_ten      = VALID_HO_TEN,
            sdt         = VALID_SDT,
            dia_chi     = VALID_DIA_CHI,
            gioi_tinh   = VALID_GIOI_TINH,
            email       = make_valid_email(),    # email mới để tránh lỗi email trùng
            ngay_sinh   = VALID_NGAY_SINH,
            tai_khoan   = "hong",               # username đã tồn tại trong DB
            mat_khau    = VALID_MAT_KHAU,
            xac_nhan_mk = VALID_MAT_KHAU,
        )
        page.scroll_to_submit_button()
        page.click_dang_ky()

        error_text = page.get_span_error_text()
        assert MSG_DUPLICATE_USERNAME in error_text, \
            f"TC-60: Expected '{MSG_DUPLICATE_USERNAME}', got '{error_text}'"

    def test_TC61_dang_ky_email_da_ton_tai(self, driver):
        
        page = open_register(driver)
        page.fill_form(
            ho_ten      = VALID_HO_TEN,
            sdt         = VALID_SDT,
            dia_chi     = VALID_DIA_CHI,
            gioi_tinh   = VALID_GIOI_TINH,
            email       = "hong@gmail.com",     # email đã tồn tại
            ngay_sinh   = VALID_NGAY_SINH,
            tai_khoan   = make_valid_username(), # username mới
            mat_khau    = VALID_MAT_KHAU,
            xac_nhan_mk = VALID_MAT_KHAU,
        )
        page.scroll_to_submit_button()
        page.click_dang_ky()

        error_text = page.get_span_error_text()
        assert MSG_DUPLICATE_EMAIL in error_text, \
            f"TC-61: Expected '{MSG_DUPLICATE_EMAIL}', got '{error_text}'"

     

