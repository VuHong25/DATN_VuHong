import pytest
from pages.login_page_new import LoginPage
from data.test_data_login import login_data
from conftest import base_url, LOGIN_PASSWORD, LOGIN_USERNAME, ADMIN_PASSWORD, ADMIN_USERNAME
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLogin:
    #access right
    #1
    def test_login_customer(self, driver):
        page = LoginPage(driver)
        page.open_login_page(base_url)

        page.login(LOGIN_USERNAME, LOGIN_PASSWORD)

        WebDriverWait(driver, 10).until(
            lambda d: "login" not in d.current_url.lower()
        )

        assert "login" not in driver.current_url.lower(), \
            "User phải đăng nhập thành công và về trang chủ"
    #2
    def test_login_admin_not_allowed(self, driver):
        page = LoginPage(driver)
        page.open_login_page(base_url)

        page.login(ADMIN_USERNAME, ADMIN_PASSWORD)

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(page.msg_error)
        )

        assert page.check_error_visible(), \
            "Admin không được phép đăng nhập"

        assert "Tài khoản hoặc mật khẩu không đúng!" in page.get_error_message(), \
            "Thông báo lỗi phải đúng theo yêu cầu"
    
    #BIZ
#15
    def test_login_success(self, driver):
        page = LoginPage(driver)
        page.open_login_page(base_url)
        page.login(LOGIN_USERNAME, LOGIN_PASSWORD)
        WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url.lower()
    )
        assert "login" not in driver.current_url.lower(), \
        "Sau khi đăng nhập thành công phải rời khỏi trang đăng nhập"
#16
    def test_login_disabled_account(self, driver):
        page = LoginPage(driver)
        page.open_login_page(base_url)

        page.login("a", "123456789")

        assert page.check_error_visible(), "Phải hiện thông báo lỗi"
        
        assert "vô hiệu hóa" in page.get_error_message().lower(), \
            "Phải hiện 'Tài khoản của bạn đã bị vô hiệu hóa!'"
        
  
    # ==========================================================
    # NHÓM: VALIDATION – Kiểm tra dữ liệu nhập vào
    # ==========================================================

    @pytest.mark.parametrize(
        "test_id, username, password, expected",
        login_data,
        ids=[d[0] for d in login_data]
    )
    def test_login_parametrize(self, driver, test_id, username, password, expected):
    
        page = LoginPage(driver)
        page.open_login_page(base_url)
        page.login(username, password)

        if expected == "success":
            WebDriverWait(driver, 10).until(
                lambda d: "login" not in d.current_url.lower()
    )
            assert "login" not in driver.current_url.lower(), \
                f"[{test_id}] Đăng nhập thành công phải rời trang login"
       
        elif expected == "html5":
            if username == "":
                assert page.is_field_invalid_html5(page.input_username), \
                    f"[{test_id}] Username phải invalid"
                
            if password == "":
                assert page.is_field_invalid_html5(page.input_password), \
                    f"[{test_id}] Password phải invalid"
            assert "login" in driver.current_url.lower(), \
                f"[{test_id}] Không được rời trang login"
            assert page.get_error_message() in ["", None], \
                f"[{test_id}] Không được có server error"
        else:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(page.msg_error)
            )
            error_text = page.get_error_message()
            assert error_text != "", "Phải có thông báo lỗi"
            assert expected in error_text, \
                f"[{test_id}] Sai message. Expected: {expected} | Got: {error_text}"
 