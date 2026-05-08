# ============================================================
# FILE: conftest.py
# MỤC ĐÍCH: Cấu hình chung cho pytest – khởi động/tắt trình duyệt
# LÝ THUYẾT – FIXTURE:
#   Fixture là "đồ dùng" được chuẩn bị sẵn trước mỗi bài test.
#   @pytest.fixture → đánh dấu một hàm là fixture.
#   scope="function" → mỗi test case tạo 1 trình duyệt riêng.
#   yield → giống như "trao" trình duyệt cho test dùng;
#           sau yield là code dọn dẹp (đóng trình duyệt).
# FILE NÀY LÀM 4 VIỆC:
#   1. Khai báo base_url và fixture driver / logged_in_driver
#   2. Tự động CHỤP ẢNH khi test FAIL
#   3. NHÚNG ẢNH vào HTML report (dùng với --html)
#   4. Thêm METADATA vào header của HTML report
# ============================================================

import pytest
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from pages.login_page_new import LoginPage
from pages.invoice_page import InvoicePage
from pages.add_to_cart_page import AddToCartPage
import os
from datetime import datetime

# địa chỉ gốc của website
base_url = "https://localhost:44392/"
# Thư mục lưu ảnh chụp khi test fail
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)    # Tạo thư mục nếu chưa có
# Thư mục lưu HTML report
os.makedirs("reports", exist_ok=True)

LOGIN_USERNAME = "test_1"
LOGIN_PASSWORD = "123456789"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

@pytest.fixture(scope="function")
def driver():
    options = Options()
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False, 
        "profile.password_manager_leak_detection": False
    }
    options.add_experimental_option("prefs", prefs)
    # 🔥 QUAN TRỌNG – thêm dòng này
    options.add_argument("--disable-save-password-bubble")

    # Tắt thêm popup/notification
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.maximize_window() # Luôn phóng to cửa sổ để tránh lỗi ẩn phần tử
    yield driver
    time.sleep(1)
    driver.quit()

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    
    page = LoginPage(driver)
    page.open_login_page(base_url)
    page.login("test_1", "123456789")
    yield driver

@pytest.fixture(scope="function")
def admin_driver(driver):
    """Đăng nhập admin và trả về driver."""

    page = InvoicePage(driver)
    page.open_admin_login(base_url)
    page.login_admin("admin", "admin")
    page.dismiss_password_warning()   # bỏ popup Chrome password manager
    yield driver


# PHẦN 2 – TỰ ĐỘNG CHỤP ẢNH + NHÚNG VÀO HTML REPORT KHI FAIL
# ==============================================================
 
# LÝ THUYẾT – HOOK:
#   pytest có "hook" = điểm móc vào vòng đời của test.
#   @pytest.hookimpl(hookwrapper=True) cho phép chạy code CẢ TRƯỚC lẫn SAU test.
#   pytest_runtest_makereport chạy sau mỗi test → đọc kết quả pass/fail.
#   Nếu FAIL → lấy driver → chụp ảnh → lưu file + nhúng vào report.@pytest.hookimpl(hookwrapper=True)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # chạy test trước
    outcome = yield
    rep = outcome.get_result()

    # gắn report vào item (quan trọng)
    setattr(item, "rep_" + rep.when, rep)

    # chỉ xử lý khi test fail
    if rep.when == "call" and rep.failed:
        driver = (
            item.funcargs.get("driver")
            or item.funcargs.get("logged_in_driver")
            or item.funcargs.get("admin_driver")
        )

        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = item.name.replace("/", "_").replace(":", "_")
            filepath = f"{SCREENSHOT_DIR}/{test_name}__{timestamp}.png"

            driver.save_screenshot(filepath)

            try:
                import pytest_html
                screenshot_b64 = driver.get_screenshot_as_base64()

                extra = getattr(rep, "extras", [])
                extra.append(pytest_html.extras.image(screenshot_b64, mime_type="image/png"))
                rep.extras = extra
            except Exception:
                pass
            # # 👉 phần pytest-html (an toàn)
            # try:
            #     import pytest_html
            #     extra = getattr(rep, "extras", [])
            #     extra.append(pytest_html.extras.image(filepath))
            #     rep.extras = extra
            # except Exception:
            #     pass
# # PHẦN 3 – METADATA CHO HTML REPORT
# # ==============================================================
 
# # LÝ THUYẾT – pytest_configure:
# #   Hook chạy 1 lần khi pytest khởi động.
# #   config._metadata = dict hiện thị ở bảng đầu trang HTML report.
# #   Giúp report trông chuyên nghiệp khi nộp hoặc demo.

def pytest_configure(config):
    # metadata HTML report
    config._metadata = {
        "Dự án"       : "Website TrueMart - Automation Test",
        "Tester"      : "Vũ Hồng", 
        "Môi trường"  : "localhost:44392",
        "Framework"   : "Selenium + pytest + POM",
        "Trình duyệt" : "Chrome (webdriver-manager)",
    }

from report_excel import ExcelReportPlugin
def pytest_configure(config):
    plugin = ExcelReportPlugin("DATN_TestCase_v1.xlsx")
    config.pluginmanager.register(plugin, "report_excel")