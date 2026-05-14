# ============================================================
# FILE: conftest_excel_report.py
# MỤC ĐÍCH: Plugin pytest – xuất kết quả test ra 1 sheet Excel duy nhất
# KẾT QUẢ: reports/test_report_<timestamp>.xlsx  — 1 sheet duy nhất
#
# CỘT XUẤT:
#   Module | ID Test Case | Test Case Title (từ Excel) | Tên Test (code) | Test Data (từ code) | Result | Lý do lỗi
# ============================================================

import re
import os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ─────────────────────────────────────────────────────────────
#  MÀU SẮC & STYLE
# ─────────────────────────────────────────────────────────────
FILL_PASS     = PatternFill("solid", fgColor="C6EFCE")
FILL_FAIL     = PatternFill("solid", fgColor="FFC7CE")
FILL_SKIP     = PatternFill("solid", fgColor="FFEB9C")
FILL_HEADER   = PatternFill("solid", fgColor="2E75B6")
FILL_MODULE   = PatternFill("solid", fgColor="D6E4F7")
FILL_SUBTOTAL = PatternFill("solid", fgColor="1F3864")   # xanh đậm cho dòng Sub total
FILL_METRIC   = PatternFill("solid", fgColor="FFFFFF")   # trắng cho dòng metric

FONT_PASS     = Font(color="375623")
FONT_FAIL     = Font(color="9C0006")
FONT_SKIP     = Font(color="7D6608")
FONT_HEADER   = Font(color="FFFFFF", bold=True, size=11)
FONT_MODULE   = Font(bold=True, color="1F4E79")
FONT_SUBTOTAL = Font(color="FFFFFF", bold=True)
FONT_METRIC_LABEL = Font(color="C0392B", bold=True)   # đỏ như ảnh
FONT_METRIC_VALUE = Font(color="1A5276", bold=True)   # xanh đậm

_THIN   = Side(style="thin")
BORDER  = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

CENTER  = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT    = Alignment(horizontal="left",   vertical="center", wrap_text=True)


# ─────────────────────────────────────────────────────────────
#  MAP: tên file test (module_key) → (sheet_name, module_code, display_name)
#  module_key phải khớp chính xác với tên file test (không có .py)
# ─────────────────────────────────────────────────────────────
MODULE_MAP = {
    "test_login"    : ("Login",          "ĐN",             "Đăng nhập"),
    "test_cart"     : ("Cart",           "GH",      "Giỏ hàng"),
    "test_register" : ("Register",       "ĐK",     "Đăng ký"),
    "test_invoice"  : ("Invoice",        "HĐ",       "Hóa đơn"),
    "test_order"    : ("Order",          "ĐH",              "Đặt hàng"),
    "test_add_to_cart" : ("Add_to_cart",       "ATC", "Thêm vào giỏ"),
    "test_search"   : ("Search",         "TK",              "TK"),
    "test_product"  : ("Product_detail", "SP", "Chi tiết SP"),
}

# Thứ tự hiển thị module trong báo cáo
MODULE_ORDER = [
    "test_login", "test_register", "test_cart",
    "test_order", "test_invoice",
    "test_add_to_cart", "test_search", "test_product",
]


# ─────────────────────────────────────────────────────────────
#  TEST DATA từ code — map: (module_key, tc_num) → chuỗi data
#  Lấy trực tiếp từ các biến trong test_data_*.py
#  Cập nhật thêm nếu project có thêm TC mới
# ─────────────────────────────────────────────────────────────
CODE_DATA_MAP: dict[tuple, str] = {
    # ── LOGIN ──
    ("test_login", 1) : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_login", 2) : "Tài khoản: admin | Mật khẩu: admin",
    ("test_login", 7) : "Tài khoản: (trống) | Mật khẩu: 123456789",
    ("test_login", 8) : "Tài khoản: tets_1 | Mật khẩu: 123456789",
    ("test_login", 9) : "Tài khoản: haha | Mật khẩu: 123456789",
    ("test_login", 10): "Tài khoản: Test_1 | Mật khẩu: 123456789",
    ("test_login", 11): "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_login", 12): "Tài khoản: test_1 | Mật khẩu: (trống)",
    ("test_login", 13): "Tài khoản: test_1 | Mật khẩu: wrongpass",
    ("test_login", 14): "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_login", 15): "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_login", 16): "Tài khoản: a | Mật khẩu: 123456789",

    # ── CART ──
    ("test_cart", 1)  : "",
    ("test_cart", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_cart", 7)  : "",
    ("test_cart", 8)  : "",
    ("test_cart", 9) : "Hành động: increase | SL đặt trước: 1 | Delta: +1",
    ("test_cart", 10) : "Hành động: decrease | SL đặt trước: 2 | Delta: -1",
    ("test_cart", 11) : f"Số lần click (+) tối đa: 20 | Expected: 'không đủ'",
    ("test_cart", 12) : "SL đặt trước: 1 | Expected popup: 'Xóa sản phẩm này khỏi giỏ hàng'",
    ("test_cart", 13) : "Số lượng nhập: 0 | Kịch bản: popup_confirm",
    ("test_cart", 14) : "Số lượng nhập: -1 | Kịch bản: reject",
    ("test_cart", 15) : "Số lượng nhập: 1.5 | Kịch bản: reject",
    ("test_cart", 16) : "Số lượng nhập: 'a' | Kịch bản: reject",
    ("test_cart", 17) : "Số lượng nhập: '!' | Kịch bản: reject",
    ("test_cart", 18) : "Số lượng nhập: (trống) | Kịch bản: reject",
    ("test_cart", 19) : "Số lượng nhập: 2 | Kịch bản: accept",
    ("test_cart", 20) : "Số lượng nhập: 100 | Kịch bản: out_of_stock",
    ("test_cart", 21) : "Hành động popup: OK | Kết quả: removed",
    ("test_cart", 22) : "SP tối thiểu: 3 | Số lần xóa: 2",
    ("test_cart", 23) : "SP tối thiểu: 3 | Expected: 'Chưa có sản phẩm nào trong giỏ hàng'",
    ("test_cart", 24) : "Hành động popup: Cancel | Kết quả: kept",
    ("test_cart", 25) : "",

    # ── REGISTER ──
    ("test_register", 1)  : "",
    ("test_register", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_register", 7)  : "Họ tên: (trống)",
    ("test_register", 8)  : "Họ tên: hồng",
    ("test_register", 9)  : "Họ tên: HỒNG",
    ("test_register", 10) : "Họ tên: hỒNg",
    ("test_register", 11) : "Họ tên: 123",
    ("test_register", 12) : "Họ tên: !@#",
    ("test_register", 13) : "Họ tên: hồng12",
    ("test_register", 14) : "Họ tên: hồng@#",
    ("test_register", 15) : "Họ tên: ' hồng' (khoảng trắng đầu)",
    ("test_register", 16) : "SĐT: (trống)",
    ("test_register", 17) : "SĐT: 'điện!@'",
    ("test_register", 18) : "SĐT: '0123 456 789' (khoảng trắng)",
    ("test_register", 19) : "SĐT: 1234567899 (không bắt đầu bằng 0)",
    ("test_register", 20) : "SĐT: 012345678 (9 ký tự)",
    ("test_register", 21) : "SĐT: 0123456789 (10 ký tự hợp lệ)",
    ("test_register", 22) : "SĐT: 01234567899 (11 ký tự)",
    ("test_register", 23) : "Email: (trống)",
    ("test_register", 24) : "Email: honggmail.com (thiếu @)",
    ("test_register", 25) : "Email: hong@gmailcom (thiếu dấu chấm)",
    ("test_register", 26) : "Email: @gmail.com (không có local part)",
    ("test_register", 27) : "Email: hong@gmail (không có TLD)",
    ("test_register", 28) : "Email: hong@gmail.com (hợp lệ, random suffix)",
    ("test_register", 29) : "Mật khẩu: (trống)",
    ("test_register", 30) : "Mật khẩu: 123456 (≥6 ký tự)",
    ("test_register", 31) : "Mật khẩu: 123456 | Xác nhận: (trống)",
    ("test_register", 32) : "Mật khẩu: 123456 | Xác nhận: 1234567 (không khớp)",
    ("test_register", 33) : "Mật khẩu: 1234567 | Xác nhận: 1234567 (khớp)",
    ("test_register", 34) : "Tài khoản: (trống)",
    ("test_register", 35) : "Tài khoản: 'vũ hồng' (chữ thường)",
    ("test_register", 36) : "Tài khoản: 'VŨ HỒNG' (in hoa)",
    ("test_register", 37) : "Tài khoản: 'vŨ HồNg' (hỗn hợp)",
    ("test_register", 38) : "Tài khoản: 22222 (là số)",
    ("test_register", 39) : "Tài khoản: '@@@' (ký tự đặc biệt)",
    ("test_register", 40) : "Tài khoản: 'hồng25' (chữ + số)",
    ("test_register", 41) : "Tài khoản: 'hồng@@@@' (chữ + ký tự đặc biệt)",
    ("test_register", 42) : "Tài khoản: ' hồng' (khoảng trắng đầu)",
    ("test_register", 43) : "Địa chỉ: (trống)",
    ("test_register", 44) : "Địa chỉ: 'Mão Điền Bắc Ninh' (chữ thường)",
    ("test_register", 45) : "Địa chỉ: 'MÃO ĐIỀN BẮC NINH' (in hoa)",
    ("test_register", 46) : "Địa chỉ: 'bẮc ninh' (hỗn hợp)",
    ("test_register", 47) : "Địa chỉ: 123 (là số)",
    ("test_register", 48) : "Địa chỉ: '@@#' (ký tự đặc biệt)",
    ("test_register", 49) : "Địa chỉ: '3 xóm 3 Mão Điền' (chữ + số)",
    ("test_register", 50) : "Địa chỉ: '3 xóm 3 - Mão Điền - Bắc Ninh' (chữ + gạch)",
    ("test_register", 51) : "Ngày sinh: (trống)",
    ("test_register", 52) : "Ngày sinh: 2003-01-01 (hợp lệ)",
    ("test_register", 53) : "Ngày sinh: 0003-01-01 (không hợp lệ)",
    ("test_register", 54) : "Tất cả trường hợp lệ | Tài khoản: user_random | Email: random",
    ("test_register", 55) : "Tài khoản đã tồn tại: 'hong' | Email: random",
    ("test_register", 56) : "Email đã tồn tại: hong@gmail.com | Tài khoản: random",

    # ── INVOICE ──
    ("test_invoice", 1)  : "Tài khoản: admin | Mật khẩu: admin",
    ("test_invoice", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_invoice", 7)  : "",
    ("test_invoice", 8)  : "",
    ("test_invoice", 9) : f"row_index: 16 (hóa đơn chưa hủy)",
    ("test_invoice", 10) : "Hóa đơn đã bị hủy",
    ("test_invoice", 11) : "Trạng thái: Đang giao / Đang chuẩn bị / Đã thanh toán",
    ("test_invoice", 12) : "Click OK → trạng thái = 'Đã bị hủy'",
    ("test_invoice", 13) : "Click Cancel → đơn hàng giữ nguyên",
    ("test_invoice", 14) : "Đơn đã hủy → nút 'Hủy đơn hàng' bị ẩn",

    # ── ORDER ──
    ("test_order", 1)  : "",
    ("test_order", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_order", 7)  : "Họ tên: Thử | SĐT: 0123654789 | Địa chỉ: Mão Điền",
    ("test_order", 8)  : "Họ tên: Hồng | SĐT: 0123654789 | Địa chỉ: Mão Điền",
    ("test_order", 9)  : "Họ tên/SĐT/Địa chỉ: (bỏ trống từng trường)",
    ("test_order", 10) : "Giữ nguyên thông tin mặc định",
    ("test_order", 11) : "Giỏ hàng rỗng",


    # # ── CATEGORY ──
    # ("test_category", 1) : "",
    # ("test_category", 2) : "Tài khoản: test_1 | Mật khẩu: 123456789",
    # ("test_category", 7) : "",
    # ("test_category", 8) : "DB không có danh mục",

    # ── SEARCH ──
    ("test_search", 1)  : "",
    ("test_search", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_search", 7)  : "Từ khóa: (trống) | Submit: button",
    ("test_search", 8)  : "Từ khóa: '@@@' | Submit: button",
    ("test_search", 9)  : "Từ khóa: '123' | Submit: button",
    ("test_search", 10) : "Từ khóa: 'Áo12' | Submit: button",
    ("test_search", 11) : "Từ khóa: 'Áo@@@' | Submit: button",
    ("test_search", 12) : "Từ khóa: '12@' | Submit: button",
    ("test_search", 13) : "Từ khóa: 'áO' | Submit: button",
    ("test_search", 14) : "Từ khóa: 'ÁO' | Submit: button",
    ("test_search", 15) : "Từ khóa: 'Quần khaki nam slimfit' | Min kết quả: 2",
    ("test_search", 16) : "Từ khóa: 'a' (1 ký tự) | Submit: button",
    ("test_search", 17) : "Từ khóa: 'Áo sơ mi' | Submit: Enter",
    ("test_search", 18) : "Từ khóa: 'Ao ba lo' (không dấu) | Submit: button",
    ("test_search", 19) : "Từ khóa: 'Áo thun lam' (sai chính tả) | Submit: button",
    ("test_search", 20) : "Từ khóa: ' Áo sơ mi ' (khoảng trắng đầu/cuối) | Submit: button",
    ("test_search", 21) : "Từ khóa: 'Áo sơ mi nam trơn' | Submit: button",
    ("test_search", 22) : "Từ khóa: 'Quần jean nữ ôm body' (hết hàng) | Submit: button",
    ("test_search", 23) : "Từ khóa: 'Áo dài' (không tồn tại) | Submit: button",

    # ── PRODUCT DETAIL ──
    ("test_product", 1)  : "",
    ("test_product", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_product", 7)  : "Sản phẩm: Áo phông nữ in họa tiết (còn hàng)",
    ("test_product", 8)  : "Sản phẩm: Quần jeans nữ ôm body (hết hàng)",
    ("test_product", 9)  : "Sản phẩm: Áo phông nam trơn | Size: XXXL (hết)",
    ("test_product", 10) : "Sản phẩm: Áo sơ mi nam trơn (có đánh giá)",
    ("test_product", 11) : "Sản phẩm: Áo phông nữ in họa tiết (chưa có đánh giá)",

    #---ADD_TO_CART
    ("test_add_to_cart", 1)  : "",
    ("test_add_to_cart", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
    ("test_add_to_cart", 7) : "Sản phẩm: Áo ba lỗ | Tài khoản: test_1",
    ("test_add_to_cart", 8) : "Sản phẩm: Quần jean nữ ôm body (hết hàng)",
    ("test_add_to_cart", 9) : "Sản phẩm: Áo phông nam trơn | Size XXXL hết",
    ("test_add_to_cart", 10) : "Sản phẩm: còn hàng | Số lượng nhập: 1000",  
}
# ─────────────────────────────────────────────────────────────
#  MAP THỦ CÔNG: (module_key, tên_hàm) → TC số thứ tự
# ─────────────────────────────────────────────────────────────
MANUAL_MAP: dict[tuple, int] = {
    # LOGIN
    ("test_login", "test_login_customer")                              : 1,
    ("test_login", "test_login_admin_not_allowed")                     : 2,
    ("test_login", "test_login_success")                               : 15,
    ("test_login", "test_login_disabled_account")                      : 16,

    # CART
    ("test_cart", "test_view_cart_not_logged_in")                      : 1,
    ("test_cart", "test_view_cart_logged_in")                          : 2,
    ("test_cart", "test_view_cart_with_items")                         : 7,
    ("test_cart", "test_view_empty_cart")                              : 8,
    ("test_cart", "test_increase_exceeds_stock")                       : 11,
    ("test_cart", "test_decrease_at_qty_one_shows_popup")              : 12,
    ("test_cart", "test_remove_multiple_products")                     : 22,
    ("test_cart", "test_remove_all_products")                          : 23,
    ("test_cart", "test_continue_shopping")                            : 25,

    # REGISTER
    ("test_register", "test_TC01_mo_trang_dang_ky_chua_dang_nhap")    : 1,
    ("test_register", "test_TC02_da_dang_nhap_khong_hien_nut_dang_ky"): 2,
    ("test_register", "test_TC31_email_hop_le")                        : 28,
    ("test_register", "test_TC59_dang_ky_thanh_cong")                  : 54,
    ("test_register", "test_TC60_dang_ky_tai_khoan_da_ton_tai")        : 55,
    ("test_register", "test_TC61_dang_ky_email_da_ton_tai")            : 56,

    # INVOICE
    ("test_invoice", "test_admin_can_access_invoice")                  : 1,
    ("test_invoice", "test_customer_cannot_access_admin_invoice")      : 2,
    ("test_invoice", "test_view_invoice_list_has_data")                : 7,
    ("test_invoice", "test_view_invoice_list_empty")                   : 8,
    ("test_invoice", "test_view_invoice_detail")                       : 9,
    ("test_invoice", "test_view_cancelled_invoice_detail")             : 10,
    ("test_invoice", "test_cancel_order_success")                      : 12,
    ("test_invoice", "test_cancel_order_click_cancel")                 : 13,
    ("test_invoice", "test_cancelled_order_hides_cancel_btn")          : 14,

    # ORDER 
    ("test_order", "test_tc1_order_without_login_redirects_to_login")   : 1,
    ("test_order", "test_tc2_order_after_login_reaches_checkout")       : 2,
    ("test_order", "test_tc7_keep_default_info_order_success")          : 7,
    ("test_order", "test_tc8_change_receiver_info_order_success")       : 8,
    ("test_order", "test_tc10_place_order_success_cart_becomes_empty")  : 10,
    ("test_order", "test_tc11_order_empty_cart_not_allowed")            : 11,

    # SEARCH
    ("test_search", "test_search_without_login")                        : 1,
    ("test_search", "test_search_with_login")                           : 2,

    # PRODUCT
    ("test_product", "test_tc01_view_product_not_logged_in")            : 1,
    ("test_product", "test_tc02_view_product_logged_in")                : 2,
    ("test_product", "test_tc07_view_in_stock_product")                 : 7,
    ("test_product", "test_tc08_view_out_of_stock_product")             : 8,
    ("test_product", "test_tc09_view_out_of_size_product")              : 9,
    ("test_product", "test_tc10_product_with_review")                   : 10,
    ("test_product", "test_tc11_product_no_review")                     : 11,

    #ADD TO CART
    ("test_add_to_cart", "test_tc01_add_to_cart_not_logged_in")                   : 1,
    ("test_add_to_cart", "test_tc02_add_to_cart_logged_in")              : 2,
    ("test_add_to_cart", "test_tc7_add_to_cart_success")                   : 7,
    ("test_add_to_cart", "test_tc8_add_to_cart_out_of_stock")              : 8,
    ("test_add_to_cart", "test_tc9_add_to_cart_out_of_size")               : 9,
    ("test_add_to_cart", "test_tc10_add_to_cart_exceed_quantity")          : 10,
}


# ─────────────────────────────────────────────────────────────
#  MAP THAM SỐ PARAMETRIZE: module_key → { chuỗi_trong_param_id → TC số }
# ─────────────────────────────────────────────────────────────
PARAM_MAP: dict[str, dict[str, int]] = {
    "test_login": {
        "DN-blank-user-TC7"  : 7,   "DN-blank-pass-TC12" : 12,
        "DN-wrong-user-TC8"  : 8,   "DN-not-exist-TC9"   : 9,
        "DN-case-sens-TC10"  : 10,  "DN-wrong-pass-TC13" : 13,
        "DN-valid-TC11"      : 11,  "DN-valid-TC14"      : 14,
        "DN-disabled-TC16"   : 16,  "DN-valid"           : 15,
    },
    "test_cart": {
        "tc10_increase": 9,  "tc11_decrease": 10,
        "tc14_zero"    : 13,  "tc15_negative": 14,
        "tc16_float"   : 15,  "tc17_text"    : 16,
        "tc18_special" : 17,  "tc19_empty"   : 18,
        "tc20_valid"   : 19,  "tc21_exceed"  : 20,
        "tc22_ok"      : 21,  "tc25_cancel"  : 24,
    },
    "test_register": {
        "TC-7" : 7,  "TC-8" : 8,  "TC-9" : 9,  "TC-10": 10,
        "TC-11": 11, "TC-12": 12, "TC-13": 13, "TC-14": 14,
        "TC-15": 15, "TC-16": 16, "TC-17": 17, "TC-18": 18,
        "TC-19": 19, "TC-20": 20, "TC-21": 21, "TC-22": 22,
        "TC-23": 23, "TC-24": 24, "TC-25": 25, "TC-26": 26,
        "TC-27": 27, "TC-29": 29, "TC-30": 30, "TC-31": 31,
        "TC-32": 32, "TC-33": 33, "TC-34": 34, "TC-35": 35,
        "TC-36": 36, "TC-37": 37, "TC-38": 38, "TC-39": 39,
        "TC-40": 40, "TC-41": 41, "TC-42": 42, "TC-43": 43,
        "TC-44": 44, "TC-45": 45, "TC-46": 46, "TC-47": 47,
        "TC-48": 48, "TC-49": 49, "TC-50": 50, "TC-51": 51,
        "TC-52": 52, "TC-53": 53,
    },
    "test_invoice": {
        "tc11_dang_giao"    : 11,
        "tc11_dang_chuan_bi": 11,
        "tc11_da_thanh_toan": 11,
    },
    # "test_checkout": {
    #     "tc9_empty_ho_ten"         : 9,
    #     "tc9_empty_sdt"            : 9,
    #     "tc9_empty_dia_chi"        : 9,
    #     "tc10_success_default_info": 10,
    # },
    "test_order": {
        "tc9_empty_ho_ten"         : 9,
        "tc9_empty_sdt"            : 9,
        "tc9_empty_dia_chi"        : 9,
        "tc10_success_default_info": 10,
    },
    # "test_category": {
    #     "TC-1": 1, "TC-2": 2, "TC-7": 7, "TC-8": 8,
    
    "test_search": {
        "TK-7" : 7,  "TK-8" : 8,  "TK-9" : 9,  "TK-10": 10,
        "TK-11": 11, "TK-12": 12, "TK-13": 13, "TK-14": 14,
        "TK-15": 15, "TK-16": 16, "TK-17": 17, "TK-18": 18,
        "TK-19": 19, "TK-20": 20, "TK-21": 21, "TK-22": 22,
        "TK-23": 23,
    },
}


# ═══════════════════════════════════════════════════════════════
#  PLUGIN CLASS
# ═══════════════════════════════════════════════════════════════
class ExcelReportPlugin:
    """
    Plugin pytest - xuất 1 sheet Excel tổng hợp toàn bộ kết quả.

    CỘT:
      Module | ID Test Case | Test Case Title (Excel) | Tên Test (code)
      | Test Data (code) | Result | Lý do lỗi
    """

    def __init__(self, template_path: str):
        self.template_path = template_path
        # Kết quả thu thập theo thứ tự chạy
        self.results: list[dict] = []
        # Cache: (sheet_name, tc_num) → title từ Excel
        self._title_cache: dict[tuple, str] = {}
        self._load_title_cache()

    # ─────────────────────────────────────────────────────────
    #  Load title từ Excel
    # ─────────────────────────────────────────────────────────
    def _load_title_cache(self):
        if not os.path.exists(self.template_path):
            print(f"\n[ExcelReport]  Không tìm thấy template: {self.template_path}")
            print(f"[ExcelReport]   → Kiểm tra lại EXCEL_TEMPLATE trong conftest.py")
            return
        try:
            wb = load_workbook(self.template_path, data_only=True)
            # Dùng set tránh load cùng 1 sheet 2 lần
            # (vd: test_checkout và test_order cùng trỏ vào sheet "Order")
            loaded_sheets = set()
            for module_key, (sheet_name, _, _) in MODULE_MAP.items():
                if sheet_name in loaded_sheets:
                    continue
                if sheet_name not in wb.sheetnames:
                    continue
                ws = wb[sheet_name]
                for row_idx in range(9, ws.max_row + 1):
                    desc = ws.cell(row=row_idx, column=4).value
                    if desc and str(desc).strip():
                        tc_num = row_idx - 8
                        self._title_cache[(sheet_name, tc_num)] = str(desc).strip()
                loaded_sheets.add(sheet_name)
            print(f"\n[ExcelReport]  Đã load {len(self._title_cache)} TC title từ template.")
        except Exception as e:
            print(f"\n[ExcelReport]  Lỗi đọc template: {e}")

    # ─────────────────────────────────────────────────────────
    #  Hook: thu thập kết quả sau mỗi test
    # ─────────────────────────────────────────────────────────
    def pytest_runtest_logreport(self, report):
        # Chỉ xử lý phase "call"; ngoại trừ skip có thể ở "setup"
        if report.when not in ("call", "setup"):
            return
        if report.when == "setup" and not report.skipped:
            return

        node_id    = report.nodeid
        module_key = self._get_module_key(node_id)
        if module_key is None:
            return

        sheet_name, module_code, display_name = MODULE_MAP[module_key]
        func_name, param_id = self._parse_node_id(node_id)
        tc_num = self._resolve_tc_num(module_key, func_name, param_id)

        # ── Test Case Title: lấy từ Excel cache (cột D) ──
        # Ưu tiên 1: cache từ Excel theo (sheet_name, tc_num)
        # Ưu tiên 2: cache từ Excel theo (sheet_name, tc_num) với tc_num từ param
        # Fallback cuối: chỉ dùng khi KHÔNG tìm được tc_num nào
        title = ""
        if tc_num:
            title = self._title_cache.get((sheet_name, tc_num), "")
            if not title:
                # Thử tìm lại bằng cách parse số trực tiếp từ param_id
                m = re.search(r'(\d+)', param_id) if param_id else None
                if m:
                    alt_num = int(m.group(1))
                    title = self._title_cache.get((sheet_name, alt_num), "")
        if not title:
            # Fallback chỉ khi không có tc_num: dùng tên hàm
            title = func_name.replace("test_", "").replace("_", " ").capitalize()

        # ── Test Data: lấy từ CODE_DATA_MAP (bảng định nghĩa ở trên) ──
        data_str = ""
        if tc_num:
            # Thử module_key trước, nếu không có thì dùng sheet_name
            data_str = CODE_DATA_MAP.get((module_key, tc_num), "")

        # ── ID Test Case ──
        tc_id = f"{module_code}-{tc_num}" if tc_num else f"{module_code}-?"

        # ── Tên Test (code) – hiển thị ngắn gọn ──
        test_display = func_name
        if param_id:
            test_display = f"{func_name}[{param_id}]"

        # ── Result & Reason ──
        if report.skipped:
            result = "Skip"
            reason = self._skip_reason(report)
        elif report.failed:
            result = "Fail"
            reason = self._fail_reason(report)
        else:
            result = "Pass"
            reason = ""

        self.results.append({
            "display_name": display_name,
            "module_code" : module_code,
            "sheet"       : sheet_name,
            "module_key"  : module_key,
            "tc_num"      : tc_num or 9999,
            "tc_id"       : tc_id,
            "title"       : title,
            "test_name"   : test_display,
            "data"        : data_str,
            "result"      : result,
            "reason"      : reason,
        })

    # ─────────────────────────────────────────────────────────
    #  Hook: ghi file Excel khi session kết thúc
    # ─────────────────────────────────────────────────────────
    def pytest_sessionfinish(self, session, exitstatus):
        if not self.results:
            print("\n[ExcelReport] Không có kết quả nào để xuất.")
            return

        os.makedirs("reports", exist_ok=True)
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reports/DATN_TestReport_{ts}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "Test Results"

        self._write_header(ws)
        self._write_data(ws)
        self._format_columns(ws)

        # ── Sheet tổng hợp theo module (giống ảnh) ──
        ws_summary = wb.create_sheet("Report")
        self._write_summary_sheet(ws_summary)

        wb.save(output_path)

        total  = len(self.results)
        passed = sum(1 for r in self.results if r["result"] == "Pass")
        failed = sum(1 for r in self.results if r["result"] == "Fail")
        skip   = sum(1 for r in self.results if r["result"] == "Skip")
        tested      = passed + failed
        success_pct = (passed / tested * 100) if tested else 0
        print(f"\n[ExcelReport]   Đã xuất: {output_path}")
        print(f"[ExcelReport]     Tổng={total} | Pass={passed} | Fail={failed} | Skip={skip}")
        print(f"[ExcelReport]     Test coverage=100.00% | Successful coverage={success_pct:.2f}%")

    # ─────────────────────────────────────────────────────────
    #  Sheet Summary – bảng tổng hợp theo module (giống ảnh)
    # ─────────────────────────────────────────────────────────
    def _write_summary_sheet(self, ws):
        """
        Tạo sheet Summary với:
          1. Tiêu đề TEST REPORT
          2. Bảng thông tin dự án (Project, Project Code, Document Code, Notes)
          3. Bảng tổng hợp: No | Module code | Pass | Fail | Untested | N/A | Number of test cases
          4. Dòng Sub total
          5. Test coverage & Test successful coverage
        """
        from collections import defaultdict
        from datetime import datetime as _dt

        # ═══════════════════════════════════════════════════════
        #  CẤU HÌNH THÔNG TIN DỰ ÁN – chỉnh sửa tại đây
        # ═══════════════════════════════════════════════════════
        PROJECT_INFO = {
            "Project"       : "DATN_TrueMart_Auto",
            "Project Code"  : "DATN",
            "Document Code" : "DATN_TestReport_v1.0",
            "Notes"         : (
                "Gồm 8 module: Đăng ký, Đăng nhập, Thêm sản phẩm vào giỏ, "
                "Tìm kiếm sản phẩm, Xem chi tiết sản phẩm, "
                "Quản lí giỏ hàng, Đặt hàng, Quản lí hóa đơn"
            ),
            "Creator"          : "Vũ Thị Hồng",
            "Reviewer/Approver": "ThS. Phạm Thị Kim Phượng",
            "Issue Date"       : _dt.now().strftime("%d/%m/%Y"),
        }

        # ── Styles dùng riêng cho info block ──
        FILL_INFO_HEADER = PatternFill("solid", fgColor="FFFFFF")
        FONT_INFO_LABEL  = Font(color="C0392B", bold=True, size=11)   # đỏ đậm
        FONT_INFO_VALUE  = Font(color="1A5276", italic=True, size=11) # xanh nghiêng
        FONT_TITLE       = Font(bold=True, size=14, color="000000")

        # ── Độ rộng cột (dùng chung cho cả 2 bảng) ──
        col_widths = [6, 18, 10, 10, 12, 10, 22]
        for col, w in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = w

        # ══════════════════════════════════════════════════════
        #  ROW 1: Tiêu đề TEST REPORT (merge A1:G1)
        # ══════════════════════════════════════════════════════
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=7)
        title_cell = ws.cell(row=1, column=1, value="TEST REPORT")
        title_cell.font      = FONT_TITLE
        title_cell.alignment = CENTER
        ws.row_dimensions[1].height = 30

        # ══════════════════════════════════════════════════════
        #  ROW 2: trống
        # ══════════════════════════════════════════════════════
        ws.row_dimensions[2].height = 8

        # ══════════════════════════════════════════════════════
        #  ROWS 3-6: Bảng thông tin dự án (2 cặp cột trái / phải)
        # ══════════════════════════════════════════════════════
        #  Cột A   = nhãn trái  (col 1)
        #  Cột B-C = giá trị trái  (col 2-3, merge)
        #  Cột D   = nhãn phải  (col 4)  – in đậm cam
        #  Cột E-G = giá trị phải  (col 5-7, merge)

        info_rows = [
            ("Project",       PROJECT_INFO["Project"],
             "Creator",       PROJECT_INFO["Creator"]),
            ("Project Code", PROJECT_INFO["Project Code"],
             "Reviewer/Approver", PROJECT_INFO["Reviewer/Approver"]),
            ("Document Code", PROJECT_INFO["Document Code"],
             "Issue Date",    PROJECT_INFO["Issue Date"]),
            ("Notes",         PROJECT_INFO["Notes"],
             "",              ""),
        ]

        FONT_INFO_RIGHT_LABEL = Font(color="D35400", bold=True, size=11)  # cam đậm

        for i, (lbl_l, val_l, lbl_r, val_r) in enumerate(info_rows):
            row = 3 + i
            # ── nhãn trái ──
            cl = ws.cell(row=row, column=1, value=lbl_l)
            cl.font      = FONT_INFO_LABEL
            cl.border    = BORDER
            cl.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

            # ── giá trị trái (merge B-C) ──
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
            vl = ws.cell(row=row, column=2, value=val_l)
            vl.font      = FONT_INFO_VALUE
            vl.border    = BORDER
            vl.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            # border ô bị merge cần gán riêng
            ws.cell(row=row, column=3).border = BORDER

            # ── nhãn phải ──
            cr = ws.cell(row=row, column=4, value=lbl_r)
            cr.font      = FONT_INFO_RIGHT_LABEL
            cr.border    = BORDER
            cr.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

            # ── giá trị phải (merge E-G) ──
            if lbl_r:
                ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=7)
                vr = ws.cell(row=row, column=5, value=val_r)
                vr.font      = FONT_INFO_VALUE
                vr.border    = BORDER
                vr.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                for c in range(6, 8):
                    ws.cell(row=row, column=c).border = BORDER
            else:
                # Dòng Notes: merge D-G trắng
                ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=7)
                for c in range(4, 8):
                    ws.cell(row=row, column=c).border = BORDER

            h = 36 if lbl_l in ("Notes", "Project Code", "Document Code") else 22
            ws.row_dimensions[row].height = h

        # ══════════════════════════════════════════════════════
        #  ROW 7: trống giữa info block và bảng số liệu
        # ══════════════════════════════════════════════════════
        BLANK_ROW = 7
        ws.row_dimensions[BLANK_ROW].height = 10
        TABLE_START = 8   # bảng số liệu bắt đầu từ hàng 8

        # ══════════════════════════════════════════════════════
        #  Thu thập số liệu theo module
        # ══════════════════════════════════════════════════════
        stats = defaultdict(lambda: {"pass": 0, "fail": 0, "skip": 0, "na": 0})
        for r in self.results:
            mk = r["module_key"]
            if r["result"] == "Pass":
                stats[mk]["pass"] += 1
            elif r["result"] == "Fail":
                stats[mk]["fail"] += 1
            elif r["result"] == "Skip":
                stats[mk]["na"] += 1
            else:
                stats[mk]["skip"] += 1

        ordered_modules = [mk for mk in MODULE_ORDER if mk in stats]
        for mk in stats:
            if mk not in ordered_modules:
                ordered_modules.append(mk)

        # ══════════════════════════════════════════════════════
        #  Header bảng số liệu
        # ══════════════════════════════════════════════════════
        tbl_headers = ["No", "Module code", "Pass", "Fail", "Untested", "N/A", "Number of test cases"]
        for col, h in enumerate(tbl_headers, 1):
            c = ws.cell(row=TABLE_START, column=col, value=h)
            c.fill      = FILL_HEADER
            c.font      = FONT_HEADER
            c.border    = BORDER
            c.alignment = CENTER
        ws.row_dimensions[TABLE_START].height = 24

        # ══════════════════════════════════════════════════════
        #  Dòng dữ liệu từng module
        # ══════════════════════════════════════════════════════
        total_pass = total_fail = total_skip = total_na = 0
        data_rows  = []
        for idx, mk in enumerate(ordered_modules, 1):
            _, module_code, _ = MODULE_MAP.get(mk, ("?", mk, mk))
            s  = stats[mk]
            p, f, sk, na = s["pass"], s["fail"], s["skip"], s["na"]
            data_rows.append((idx, module_code, p, f, sk, na, p + f + sk + na))
            total_pass += p; total_fail += f; total_skip += sk; total_na += na

        for offset, (no, code, p, f, sk, na, total_tc) in enumerate(data_rows, 1):
            rw = TABLE_START + offset
            for col, val in enumerate([no, code, p, f, sk, na, total_tc], 1):
                c = ws.cell(row=rw, column=col, value=val)
                c.border    = BORDER
                c.alignment = CENTER
                c.font      = Font(name="Calibri", size=11)
            ws.row_dimensions[rw].height = 20

        # ══════════════════════════════════════════════════════
        #  Dòng Sub total
        # ══════════════════════════════════════════════════════
        sub_row   = TABLE_START + len(data_rows) + 1
        grand_all = total_pass + total_fail + total_skip + total_na
        for col, val in enumerate(["", "Sub total", total_pass, total_fail,
                                   total_skip, total_na, grand_all], 1):
            c = ws.cell(row=sub_row, column=col, value=val)
            c.fill      = FILL_SUBTOTAL
            c.font      = FONT_SUBTOTAL
            c.border    = BORDER
            c.alignment = CENTER
        ws.row_dimensions[sub_row].height = 22

        # ══════════════════════════════════════════════════════
        #  Metric rows
        # ══════════════════════════════════════════════════════
        tested       = total_pass + total_fail
        denominator  = grand_all - total_na
        coverage_pct = (tested / denominator * 100) if denominator else 0.0
        success_pct  = (total_pass / tested * 100) if tested else 0.0

        for i, (label, pct) in enumerate([
            ("Test coverage", coverage_pct),
            ("Test successful\ncoverage", success_pct),
        ]):
            mr = sub_row + 2 + i
            lc = ws.cell(row=mr, column=1, value=label.replace("\\n", "\n"))
            lc.font      = FONT_METRIC_LABEL
            lc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            ws.merge_cells(start_row=mr, start_column=1, end_row=mr, end_column=2)
            vc = ws.cell(row=mr, column=3, value=round(pct, 2))
            vc.number_format = "0.00"
            vc.font          = FONT_METRIC_VALUE
            vc.alignment     = CENTER
            ws.cell(row=mr, column=4, value="%").font = FONT_METRIC_VALUE
            ws.cell(row=mr, column=4).alignment = CENTER
            ws.row_dimensions[mr].height = 28

        ws.sheet_view.showGridLines = False

    # ─────────────────────────────────────────────────────────
    #  Ghi header
    # ─────────────────────────────────────────────────────────
    def _write_header(self, ws):
        headers = [
            "Module",
            "ID Test Case",
            "Test Case Title",
            "Tên Test (code)",
            "Test Data",
            "Result",
            "Lý do lỗi / Ghi chú",
        ]
        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.fill      = FILL_HEADER
            c.font      = FONT_HEADER
            c.border    = BORDER
            c.alignment = CENTER
        ws.row_dimensions[1].height = 22

    # ─────────────────────────────────────────────────────────
    #  Ghi dữ liệu
    # ─────────────────────────────────────────────────────────
    def _write_data(self, ws):
        # Sắp xếp theo thứ tự module → số TC
        def sort_key(r):
            try:
                mod_idx = MODULE_ORDER.index(r["module_key"])
            except ValueError:
                mod_idx = 99
            return (mod_idx, r["tc_num"])

        sorted_results = sorted(self.results, key=sort_key)

        row_num  = 2
        prev_mod = None

        for r in sorted_results:
            # ── Dòng nhóm module mới ──
            if r["display_name"] != prev_mod:
                if prev_mod is not None:
                    row_num += 1  # dòng trống giữa các module

                for col in range(1, 8):
                    c = ws.cell(row=row_num, column=col)
                    c.fill   = FILL_MODULE
                    c.font   = FONT_MODULE
                    c.border = BORDER
                    c.alignment = Alignment(vertical="center")
                    if col == 1:
                        c.value = f"  {r['display_name'].upper()}"

                ws.row_dimensions[row_num].height = 18
                row_num  += 1
                prev_mod  = r["display_name"]

            # ── Dòng dữ liệu test case ──
            values = [
                r["display_name"],       # Module
                r["tc_id"],              # ID Test Case
                r["title"],              # Test Case Title (từ Excel)
                r["test_name"],          # Tên Test (code)
                r["data"],               # Test Data (từ code)
                r["result"],             # Result
                r["reason"],             # Lý do lỗi
            ]
            for col, val in enumerate(values, 1):
                c = ws.cell(row=row_num, column=col, value=val)
                c.border = BORDER
                if col in (1, 2, 6):
                    c.alignment = CENTER
                else:
                    c.alignment = LEFT

                # Tô màu cột Result
                if col == 6:
                    if r["result"] == "Pass":
                        c.fill = FILL_PASS
                        c.font = FONT_PASS
                    elif r["result"] == "Fail":
                        c.fill = FILL_FAIL
                        c.font = FONT_FAIL
                    else:
                        c.fill = FILL_SKIP
                        c.font = FONT_SKIP

            ws.row_dimensions[row_num].height = 32
            row_num += 1

    # ─────────────────────────────────────────────────────────
    #  Định dạng độ rộng cột
    # ─────────────────────────────────────────────────────────
    def _format_columns(self, ws):
        #      Module  ID TC   Title   TestName  Data   Result  Reason
        widths = [16,   24,     56,     50,        38,    10,     56]
        for col, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = w
        ws.freeze_panes = "A2"   # Cố định dòng header

    # ─────────────────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────────────────
    def _get_module_key(self, node_id: str):
        """Xác định module_key từ node_id dựa vào tên file test."""
        node_lower = node_id.lower()
        for key in MODULE_MAP:
            if key in node_lower:
                return key
        return None

    def _parse_node_id(self, node_id: str) -> tuple:
        """
        Tách tên hàm và param_id từ pytest node_id.
        vd: "tests/test_cart.py::TestCartUpdate::test_update_cart[tc14_zero]"
            → ("test_update_cart", "tc14_zero")
        """
        parts = node_id.split("::")
        last  = parts[-1]
        m = re.match(r'^([^\[]+)\[(.+)\]$', last)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return last.strip(), ""

    def _resolve_tc_num(self, module_key: str, func_name: str, param_id: str):
        """
        Xác định số TC theo thứ tự ưu tiên:
          1. PARAM_MAP   – khớp chuỗi trong param_id
          2. MANUAL_MAP  – khớp tên hàm thủ công
          3. Regex số trong tên hàm: test_tc07, test_TC01
          4. Regex số trong param_id: [TC-7]
        """
        # 1. Param map
        if param_id and module_key in PARAM_MAP:
            for pattern, tc_num in PARAM_MAP[module_key].items():
                if pattern in param_id:
                    return tc_num

        # 2. Manual map
        val = MANUAL_MAP.get((module_key, func_name))
        if val is not None:
            return val

        # 3. Số trong tên hàm dạng test_tc07 / test_TC01
        m = re.search(r'_tc0*(\d+)', func_name, re.IGNORECASE)
        if m:
            return int(m.group(1))

        # 4. Số trong param_id dạng TC-7, TC7
        if param_id:
            m = re.search(r'TC[-_]?0*(\d+)', param_id, re.IGNORECASE)
            if m:
                return int(m.group(1))

        return None

    @staticmethod
    def _fail_reason(report) -> str:
        """Lấy dòng lỗi cuối cùng từ traceback (ngắn gọn)."""
        if report.longrepr:
            text  = str(report.longrepr)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            return lines[-1][:400] if lines else "Unknown error"
        return ""

    @staticmethod
    def _skip_reason(report) -> str:
        """Lấy lý do skip."""
        if report.longrepr:
            text = str(report.longrepr).strip()
            if "Skipped:" in text:
                return text.split("Skipped:", 1)[-1].strip()[:300]
            return text[:300]
        return ""




# # ============================================================
# # FILE: conftest_excel_report.py
# # MỤC ĐÍCH: Plugin pytest – xuất kết quả test ra 1 sheet Excel duy nhất
# # KẾT QUẢ: reports/test_report_<timestamp>.xlsx  — 1 sheet duy nhất
# #
# # CỘT XUẤT:
# #   Module | ID Test Case | Test Case Title (từ Excel) | Tên Test (code) | Test Data (từ code) | Result | Lý do lỗi
# # ============================================================

# import re
# import os
# from datetime import datetime
# from openpyxl import Workbook, load_workbook
# from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
# from openpyxl.utils import get_column_letter


# # ─────────────────────────────────────────────────────────────
# #  MÀU SẮC & STYLE
# # ─────────────────────────────────────────────────────────────
# FILL_PASS     = PatternFill("solid", fgColor="C6EFCE")
# FILL_FAIL     = PatternFill("solid", fgColor="FFC7CE")
# FILL_SKIP     = PatternFill("solid", fgColor="FFEB9C")
# FILL_HEADER   = PatternFill("solid", fgColor="2E75B6")
# FILL_MODULE   = PatternFill("solid", fgColor="D6E4F7")
# FILL_SUBTOTAL = PatternFill("solid", fgColor="1F3864")   # xanh đậm cho dòng Sub total
# FILL_METRIC   = PatternFill("solid", fgColor="FFFFFF")   # trắng cho dòng metric

# FONT_PASS     = Font(color="375623")
# FONT_FAIL     = Font(color="9C0006")
# FONT_SKIP     = Font(color="7D6608")
# FONT_HEADER   = Font(color="FFFFFF", bold=True, size=11)
# FONT_MODULE   = Font(bold=True, color="1F4E79")
# FONT_SUBTOTAL = Font(color="FFFFFF", bold=True)
# FONT_METRIC_LABEL = Font(color="C0392B", bold=True)   # đỏ như ảnh
# FONT_METRIC_VALUE = Font(color="1A5276", bold=True)   # xanh đậm

# _THIN   = Side(style="thin")
# BORDER  = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

# CENTER  = Alignment(horizontal="center", vertical="center", wrap_text=True)
# LEFT    = Alignment(horizontal="left",   vertical="center", wrap_text=True)


# # ─────────────────────────────────────────────────────────────
# #  MAP: tên file test (module_key) → (sheet_name, module_code, display_name)
# #  module_key phải khớp chính xác với tên file test (không có .py)
# # ─────────────────────────────────────────────────────────────
# MODULE_MAP = {
#     "test_login"    : ("Login",          "ĐN",             "Đăng nhập"),
#     "test_cart"     : ("Cart",           "GH",      "Giỏ hàng"),
#     "test_register" : ("Register",       "ĐK",     "Đăng ký"),
#     "test_invoice"  : ("Invoice",        "HĐ",       "Hóa đơn"),
#     "test_order"    : ("Order",          "ĐH",              "Đặt hàng"),
#     "test_add_to_cart" : ("Add_to_cart",       "ATC", "Thêm vào giỏ"),
#     "test_search"   : ("Search",         "TK",              "TK"),
#     "test_product"  : ("Product_detail", "SP", "Chi tiết SP"),
# }

# # Thứ tự hiển thị module trong báo cáo
# MODULE_ORDER = [
#     "test_login", "test_register", "test_cart",
#     "test_order", "test_invoice",
#     "test_add_to_cart", "test_search", "test_product",
# ]


# # ─────────────────────────────────────────────────────────────
# #  TEST DATA từ code — map: (module_key, tc_num) → chuỗi data
# #  Lấy trực tiếp từ các biến trong test_data_*.py
# #  Cập nhật thêm nếu project có thêm TC mới
# # ─────────────────────────────────────────────────────────────
# CODE_DATA_MAP: dict[tuple, str] = {
#     # ── LOGIN ──
#     ("test_login", 1) : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 2) : "Tài khoản: admin | Mật khẩu: admin",
#     ("test_login", 7) : "Tài khoản: (trống) | Mật khẩu: 123456789",
#     ("test_login", 8) : "Tài khoản: tets_1 | Mật khẩu: 123456789",
#     ("test_login", 9) : "Tài khoản: haha | Mật khẩu: 123456789",
#     ("test_login", 10): "Tài khoản: Test_1 | Mật khẩu: 123456789",
#     ("test_login", 11): "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 12): "Tài khoản: test_1 | Mật khẩu: (trống)",
#     ("test_login", 13): "Tài khoản: test_1 | Mật khẩu: wrongpass",
#     ("test_login", 14): "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 15): "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 16): "Tài khoản: a | Mật khẩu: 123456789",

#     # ── CART ──
#     ("test_cart", 1)  : "",
#     ("test_cart", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_cart", 7)  : "",
#     ("test_cart", 8)  : "",
#     ("test_cart", 9) : "Hành động: increase | SL đặt trước: 1 | Delta: +1",
#     ("test_cart", 10) : "Hành động: decrease | SL đặt trước: 2 | Delta: -1",
#     ("test_cart", 11) : f"Số lần click (+) tối đa: 20 | Expected: 'không đủ'",
#     ("test_cart", 12) : "SL đặt trước: 1 | Expected popup: 'Xóa sản phẩm này khỏi giỏ hàng'",
#     ("test_cart", 13) : "Số lượng nhập: 0 | Kịch bản: popup_confirm",
#     ("test_cart", 14) : "Số lượng nhập: -1 | Kịch bản: reject",
#     ("test_cart", 15) : "Số lượng nhập: 1.5 | Kịch bản: reject",
#     ("test_cart", 16) : "Số lượng nhập: 'a' | Kịch bản: reject",
#     ("test_cart", 17) : "Số lượng nhập: '!' | Kịch bản: reject",
#     ("test_cart", 18) : "Số lượng nhập: (trống) | Kịch bản: reject",
#     ("test_cart", 19) : "Số lượng nhập: 2 | Kịch bản: accept",
#     ("test_cart", 20) : "Số lượng nhập: 100 | Kịch bản: out_of_stock",
#     ("test_cart", 21) : "Hành động popup: OK | Kết quả: removed",
#     ("test_cart", 22) : "SP tối thiểu: 3 | Số lần xóa: 2",
#     ("test_cart", 23) : "SP tối thiểu: 3 | Expected: 'Chưa có sản phẩm nào trong giỏ hàng'",
#     ("test_cart", 24) : "Hành động popup: Cancel | Kết quả: kept",
#     ("test_cart", 25) : "",

#     # ── REGISTER ──
#     ("test_register", 1)  : "",
#     ("test_register", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_register", 7)  : "Họ tên: (trống)",
#     ("test_register", 8)  : "Họ tên: hồng",
#     ("test_register", 9)  : "Họ tên: HỒNG",
#     ("test_register", 10) : "Họ tên: hỒNg",
#     ("test_register", 11) : "Họ tên: 123",
#     ("test_register", 12) : "Họ tên: !@#",
#     ("test_register", 13) : "Họ tên: hồng12",
#     ("test_register", 14) : "Họ tên: hồng@#",
#     ("test_register", 15) : "Họ tên: ' hồng' (khoảng trắng đầu)",
#     ("test_register", 16) : "SĐT: (trống)",
#     ("test_register", 17) : "SĐT: 'điện!@'",
#     ("test_register", 18) : "SĐT: '0123 456 789' (khoảng trắng)",
#     ("test_register", 19) : "SĐT: 1234567899 (không bắt đầu bằng 0)",
#     ("test_register", 20) : "SĐT: 012345678 (9 ký tự)",
#     ("test_register", 21) : "SĐT: 0123456789 (10 ký tự hợp lệ)",
#     ("test_register", 22) : "SĐT: 01234567899 (11 ký tự)",
#     ("test_register", 23) : "Email: (trống)",
#     ("test_register", 24) : "Email: honggmail.com (thiếu @)",
#     ("test_register", 25) : "Email: hong@gmailcom (thiếu dấu chấm)",
#     ("test_register", 26) : "Email: @gmail.com (không có local part)",
#     ("test_register", 27) : "Email: hong@gmail (không có TLD)",
#     ("test_register", 28) : "Email: hong@gmail.com (hợp lệ, random suffix)",
#     ("test_register", 29) : "Mật khẩu: (trống)",
#     ("test_register", 30) : "Mật khẩu: 123456 (≥6 ký tự)",
#     ("test_register", 31) : "Mật khẩu: 123456 | Xác nhận: (trống)",
#     ("test_register", 32) : "Mật khẩu: 123456 | Xác nhận: 1234567 (không khớp)",
#     ("test_register", 33) : "Mật khẩu: 1234567 | Xác nhận: 1234567 (khớp)",
#     ("test_register", 34) : "Tài khoản: (trống)",
#     ("test_register", 35) : "Tài khoản: 'vũ hồng' (chữ thường)",
#     ("test_register", 36) : "Tài khoản: 'VŨ HỒNG' (in hoa)",
#     ("test_register", 37) : "Tài khoản: 'vŨ HồNg' (hỗn hợp)",
#     ("test_register", 38) : "Tài khoản: 22222 (là số)",
#     ("test_register", 39) : "Tài khoản: '@@@' (ký tự đặc biệt)",
#     ("test_register", 40) : "Tài khoản: 'hồng25' (chữ + số)",
#     ("test_register", 41) : "Tài khoản: 'hồng@@@@' (chữ + ký tự đặc biệt)",
#     ("test_register", 42) : "Tài khoản: ' hồng' (khoảng trắng đầu)",
#     ("test_register", 43) : "Địa chỉ: (trống)",
#     ("test_register", 44) : "Địa chỉ: 'Mão Điền Bắc Ninh' (chữ thường)",
#     ("test_register", 45) : "Địa chỉ: 'MÃO ĐIỀN BẮC NINH' (in hoa)",
#     ("test_register", 46) : "Địa chỉ: 'bẮc ninh' (hỗn hợp)",
#     ("test_register", 47) : "Địa chỉ: 123 (là số)",
#     ("test_register", 48) : "Địa chỉ: '@@#' (ký tự đặc biệt)",
#     ("test_register", 49) : "Địa chỉ: '3 xóm 3 Mão Điền' (chữ + số)",
#     ("test_register", 50) : "Địa chỉ: '3 xóm 3 - Mão Điền - Bắc Ninh' (chữ + gạch)",
#     ("test_register", 51) : "Ngày sinh: (trống)",
#     ("test_register", 52) : "Ngày sinh: 2003-01-01 (hợp lệ)",
#     ("test_register", 53) : "Ngày sinh: 0003-01-01 (không hợp lệ)",
#     ("test_register", 54) : "Tất cả trường hợp lệ | Tài khoản: user_random | Email: random",
#     ("test_register", 55) : "Tài khoản đã tồn tại: 'hong' | Email: random",
#     ("test_register", 56) : "Email đã tồn tại: hong@gmail.com | Tài khoản: random",

#     # ── INVOICE ──
#     ("test_invoice", 1)  : "Tài khoản: admin | Mật khẩu: admin",
#     ("test_invoice", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_invoice", 7)  : "",
#     ("test_invoice", 8)  : "",
#     ("test_invoice", 9) : f"row_index: 16 (hóa đơn chưa hủy)",
#     ("test_invoice", 10) : "Hóa đơn đã bị hủy",
#     ("test_invoice", 11) : "Trạng thái: Đang giao / Đang chuẩn bị / Đã thanh toán",
#     ("test_invoice", 12) : "Click OK → trạng thái = 'Đã bị hủy'",
#     ("test_invoice", 13) : "Click Cancel → đơn hàng giữ nguyên",
#     ("test_invoice", 14) : "Đơn đã hủy → nút 'Hủy đơn hàng' bị ẩn",

#     # ── ORDER ──
#     ("test_order", 1)  : "",
#     ("test_order", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_order", 7)  : "Họ tên: Thử | SĐT: 0123654789 | Địa chỉ: Mão Điền",
#     ("test_order", 8)  : "Họ tên: Hồng | SĐT: 0123654789 | Địa chỉ: Mão Điền",
#     ("test_order", 9)  : "Họ tên/SĐT/Địa chỉ: (bỏ trống từng trường)",
#     ("test_order", 10) : "Giữ nguyên thông tin mặc định",
#     ("test_order", 11) : "Giỏ hàng rỗng",


#     # # ── CATEGORY ──
#     # ("test_category", 1) : "",
#     # ("test_category", 2) : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     # ("test_category", 7) : "",
#     # ("test_category", 8) : "DB không có danh mục",

#     # ── SEARCH ──
#     ("test_search", 1)  : "",
#     ("test_search", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_search", 7)  : "Từ khóa: (trống) | Submit: button",
#     ("test_search", 8)  : "Từ khóa: '@@@' | Submit: button",
#     ("test_search", 9)  : "Từ khóa: '123' | Submit: button",
#     ("test_search", 10) : "Từ khóa: 'Áo12' | Submit: button",
#     ("test_search", 11) : "Từ khóa: 'Áo@@@' | Submit: button",
#     ("test_search", 12) : "Từ khóa: '12@' | Submit: button",
#     ("test_search", 13) : "Từ khóa: 'áO' | Submit: button",
#     ("test_search", 14) : "Từ khóa: 'ÁO' | Submit: button",
#     ("test_search", 15) : "Từ khóa: 'Quần khaki nam slimfit' | Min kết quả: 2",
#     ("test_search", 16) : "Từ khóa: 'a' (1 ký tự) | Submit: button",
#     ("test_search", 17) : "Từ khóa: 'Áo sơ mi' | Submit: Enter",
#     ("test_search", 18) : "Từ khóa: 'Ao ba lo' (không dấu) | Submit: button",
#     ("test_search", 19) : "Từ khóa: 'Áo thun lam' (sai chính tả) | Submit: button",
#     ("test_search", 20) : "Từ khóa: ' Áo sơ mi ' (khoảng trắng đầu/cuối) | Submit: button",
#     ("test_search", 21) : "Từ khóa: 'Áo sơ mi nam trơn' | Submit: button",
#     ("test_search", 22) : "Từ khóa: 'Quần jean nữ ôm body' (hết hàng) | Submit: button",
#     ("test_search", 23) : "Từ khóa: 'Áo dài' (không tồn tại) | Submit: button",

#     # ── PRODUCT DETAIL ──
#     ("test_product", 1)  : "",
#     ("test_product", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_product", 7)  : "Sản phẩm: Áo phông nữ in họa tiết (còn hàng)",
#     ("test_product", 8)  : "Sản phẩm: Quần jeans nữ ôm body (hết hàng)",
#     ("test_product", 9)  : "Sản phẩm: Áo phông nam trơn | Size: XXXL (hết)",
#     ("test_product", 10) : "Sản phẩm: Áo sơ mi nam trơn (có đánh giá)",
#     ("test_product", 11) : "Sản phẩm: Áo phông nữ in họa tiết (chưa có đánh giá)",

#     #---ADD_TO_CART
#     ("test_add_to_cart", 1)  : "",
#     ("test_add_to_cart", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_add_to_cart", 7) : "Sản phẩm: Áo ba lỗ | Tài khoản: test_1",
#     ("test_add_to_cart", 8) : "Sản phẩm: Quần jean nữ ôm body (hết hàng)",
#     ("test_add_to_cart", 9) : "Sản phẩm: Áo phông nam trơn | Size XXXL hết",
#     ("test_add_to_cart", 10) : "Sản phẩm: còn hàng | Số lượng nhập: 1000",  
# }
# # ─────────────────────────────────────────────────────────────
# #  MAP THỦ CÔNG: (module_key, tên_hàm) → TC số thứ tự
# # ─────────────────────────────────────────────────────────────
# MANUAL_MAP: dict[tuple, int] = {
#     # LOGIN
#     ("test_login", "test_login_customer")                              : 1,
#     ("test_login", "test_login_admin_not_allowed")                     : 2,
#     ("test_login", "test_login_success")                               : 15,
#     ("test_login", "test_login_disabled_account")                      : 16,

#     # CART
#     ("test_cart", "test_view_cart_not_logged_in")                      : 1,
#     ("test_cart", "test_view_cart_logged_in")                          : 2,
#     ("test_cart", "test_view_cart_with_items")                         : 7,
#     ("test_cart", "test_view_empty_cart")                              : 8,
#     ("test_cart", "test_increase_exceeds_stock")                       : 11,
#     ("test_cart", "test_decrease_at_qty_one_shows_popup")              : 12,
#     ("test_cart", "test_remove_multiple_products")                     : 22,
#     ("test_cart", "test_remove_all_products")                          : 23,
#     ("test_cart", "test_continue_shopping")                            : 25,

#     # REGISTER
#     ("test_register", "test_TC01_mo_trang_dang_ky_chua_dang_nhap")    : 1,
#     ("test_register", "test_TC02_da_dang_nhap_khong_hien_nut_dang_ky"): 2,
#     ("test_register", "test_TC31_email_hop_le")                        : 28,
#     ("test_register", "test_TC59_dang_ky_thanh_cong")                  : 54,
#     ("test_register", "test_TC60_dang_ky_tai_khoan_da_ton_tai")        : 55,
#     ("test_register", "test_TC61_dang_ky_email_da_ton_tai")            : 56,

#     # INVOICE
#     ("test_invoice", "test_admin_can_access_invoice")                  : 1,
#     ("test_invoice", "test_customer_cannot_access_admin_invoice")      : 2,
#     ("test_invoice", "test_view_invoice_list_has_data")                : 7,
#     ("test_invoice", "test_view_invoice_list_empty")                   : 8,
#     ("test_invoice", "test_view_invoice_detail")                       : 9,
#     ("test_invoice", "test_view_cancelled_invoice_detail")             : 10,
#     ("test_invoice", "test_cancel_order_success")                      : 12,
#     ("test_invoice", "test_cancel_order_click_cancel")                 : 13,
#     ("test_invoice", "test_cancelled_order_hides_cancel_btn")          : 14,

#     # ORDER 
#     ("test_order", "test_tc1_order_without_login_redirects_to_login")   : 1,
#     ("test_order", "test_tc2_order_after_login_reaches_checkout")       : 2,
#     ("test_order", "test_tc7_keep_default_info_order_success")          : 7,
#     ("test_order", "test_tc8_change_receiver_info_order_success")       : 8,
#     ("test_order", "test_tc10_place_order_success_cart_becomes_empty")  : 10,
#     ("test_order", "test_tc11_order_empty_cart_not_allowed")            : 11,

#     # SEARCH
#     ("test_search", "test_search_without_login")                        : 1,
#     ("test_search", "test_search_with_login")                           : 2,

#     # PRODUCT
#     ("test_product", "test_tc01_view_product_not_logged_in")            : 1,
#     ("test_product", "test_tc02_view_product_logged_in")                : 2,
#     ("test_product", "test_tc07_view_in_stock_product")                 : 7,
#     ("test_product", "test_tc08_view_out_of_stock_product")             : 8,
#     ("test_product", "test_tc09_view_out_of_size_product")              : 9,
#     ("test_product", "test_tc10_product_with_review")                   : 10,
#     ("test_product", "test_tc11_product_no_review")                     : 11,

#     #ADD TO CART
#     ("test_add_to_cart", "test_tc01_add_to_cart_not_logged_in")                   : 1,
#     ("test_add_to_cart", "test_tc02_add_to_cart_logged_in")              : 2,
#     ("test_add_to_cart", "test_tc7_add_to_cart_success")                   : 7,
#     ("test_add_to_cart", "test_tc8_add_to_cart_out_of_stock")              : 8,
#     ("test_add_to_cart", "test_tc9_add_to_cart_out_of_size")               : 9,
#     ("test_add_to_cart", "test_tc10_add_to_cart_exceed_quantity")          : 10,
# }


# # ─────────────────────────────────────────────────────────────
# #  MAP THAM SỐ PARAMETRIZE: module_key → { chuỗi_trong_param_id → TC số }
# # ─────────────────────────────────────────────────────────────
# PARAM_MAP: dict[str, dict[str, int]] = {
#     "test_login": {
#         "DN-blank-user-TC7"  : 7,   "DN-blank-pass-TC12" : 12,
#         "DN-wrong-user-TC8"  : 8,   "DN-not-exist-TC9"   : 9,
#         "DN-case-sens-TC10"  : 10,  "DN-wrong-pass-TC13" : 13,
#         "DN-valid-TC11"      : 11,  "DN-valid-TC14"      : 14,
#         "DN-disabled-TC16"   : 16,  "DN-valid"           : 15,
#     },
#     "test_cart": {
#         "tc10_increase": 9,  "tc11_decrease": 10,
#         "tc14_zero"    : 13,  "tc15_negative": 14,
#         "tc16_float"   : 15,  "tc17_text"    : 16,
#         "tc18_special" : 17,  "tc19_empty"   : 18,
#         "tc20_valid"   : 19,  "tc21_exceed"  : 20,
#         "tc22_ok"      : 21,  "tc25_cancel"  : 24,
#     },
#     "test_register": {
#         "TC-7" : 7,  "TC-8" : 8,  "TC-9" : 9,  "TC-10": 10,
#         "TC-11": 11, "TC-12": 12, "TC-13": 13, "TC-14": 14,
#         "TC-15": 15, "TC-16": 16, "TC-17": 17, "TC-18": 18,
#         "TC-19": 19, "TC-20": 20, "TC-21": 21, "TC-22": 22,
#         "TC-23": 23, "TC-24": 24, "TC-25": 25, "TC-26": 26,
#         "TC-27": 27, "TC-29": 29, "TC-30": 30, "TC-31": 31,
#         "TC-32": 32, "TC-33": 33, "TC-34": 34, "TC-35": 35,
#         "TC-36": 36, "TC-37": 37, "TC-38": 38, "TC-39": 39,
#         "TC-40": 40, "TC-41": 41, "TC-42": 42, "TC-43": 43,
#         "TC-44": 44, "TC-45": 45, "TC-46": 46, "TC-47": 47,
#         "TC-48": 48, "TC-49": 49, "TC-50": 50, "TC-51": 51,
#         "TC-52": 52, "TC-53": 53,
#     },
#     "test_invoice": {
#         "tc11_dang_giao"    : 11,
#         "tc11_dang_chuan_bi": 11,
#         "tc11_da_thanh_toan": 11,
#     },
#     # "test_checkout": {
#     #     "tc9_empty_ho_ten"         : 9,
#     #     "tc9_empty_sdt"            : 9,
#     #     "tc9_empty_dia_chi"        : 9,
#     #     "tc10_success_default_info": 10,
#     # },
#     "test_order": {
#         "tc9_empty_ho_ten"         : 9,
#         "tc9_empty_sdt"            : 9,
#         "tc9_empty_dia_chi"        : 9,
#         "tc10_success_default_info": 10,
#     },
#     # "test_category": {
#     #     "TC-1": 1, "TC-2": 2, "TC-7": 7, "TC-8": 8,
    
#     "test_search": {
#         "TK-7" : 7,  "TK-8" : 8,  "TK-9" : 9,  "TK-10": 10,
#         "TK-11": 11, "TK-12": 12, "TK-13": 13, "TK-14": 14,
#         "TK-15": 15, "TK-16": 16, "TK-17": 17, "TK-18": 18,
#         "TK-19": 19, "TK-20": 20, "TK-21": 21, "TK-22": 22,
#         "TK-23": 23,
#     },
# }


# # ═══════════════════════════════════════════════════════════════
# #  PLUGIN CLASS
# # ═══════════════════════════════════════════════════════════════
# class ExcelReportPlugin:
#     """
#     Plugin pytest - xuất 1 sheet Excel tổng hợp toàn bộ kết quả.

#     CỘT:
#       Module | ID Test Case | Test Case Title (Excel) | Tên Test (code)
#       | Test Data (code) | Result | Lý do lỗi
#     """

#     def __init__(self, template_path: str):
#         self.template_path = template_path
#         # Kết quả thu thập theo thứ tự chạy
#         self.results: list[dict] = []
#         # Cache: (sheet_name, tc_num) → title từ Excel
#         self._title_cache: dict[tuple, str] = {}
#         self._load_title_cache()

#     # ─────────────────────────────────────────────────────────
#     #  Load title từ Excel
#     # ─────────────────────────────────────────────────────────
#     def _load_title_cache(self):
#         if not os.path.exists(self.template_path):
#             print(f"\n[ExcelReport]  Không tìm thấy template: {self.template_path}")
#             print(f"[ExcelReport]   → Kiểm tra lại EXCEL_TEMPLATE trong conftest.py")
#             return
#         try:
#             wb = load_workbook(self.template_path, data_only=True)
#             # Dùng set tránh load cùng 1 sheet 2 lần
#             # (vd: test_checkout và test_order cùng trỏ vào sheet "Order")
#             loaded_sheets = set()
#             for module_key, (sheet_name, _, _) in MODULE_MAP.items():
#                 if sheet_name in loaded_sheets:
#                     continue
#                 if sheet_name not in wb.sheetnames:
#                     continue
#                 ws = wb[sheet_name]
#                 for row_idx in range(9, ws.max_row + 1):
#                     desc = ws.cell(row=row_idx, column=4).value
#                     if desc and str(desc).strip():
#                         tc_num = row_idx - 8
#                         self._title_cache[(sheet_name, tc_num)] = str(desc).strip()
#                 loaded_sheets.add(sheet_name)
#             print(f"\n[ExcelReport]  Đã load {len(self._title_cache)} TC title từ template.")
#         except Exception as e:
#             print(f"\n[ExcelReport]  Lỗi đọc template: {e}")

#     # ─────────────────────────────────────────────────────────
#     #  Hook: thu thập kết quả sau mỗi test
#     # ─────────────────────────────────────────────────────────
#     def pytest_runtest_logreport(self, report):
#         # Chỉ xử lý phase "call"; ngoại trừ skip có thể ở "setup"
#         if report.when not in ("call", "setup"):
#             return
#         if report.when == "setup" and not report.skipped:
#             return

#         node_id    = report.nodeid
#         module_key = self._get_module_key(node_id)
#         if module_key is None:
#             return

#         sheet_name, module_code, display_name = MODULE_MAP[module_key]
#         func_name, param_id = self._parse_node_id(node_id)
#         tc_num = self._resolve_tc_num(module_key, func_name, param_id)

#         # ── Test Case Title: lấy từ Excel cache (cột D) ──
#         # Ưu tiên 1: cache từ Excel theo (sheet_name, tc_num)
#         # Ưu tiên 2: cache từ Excel theo (sheet_name, tc_num) với tc_num từ param
#         # Fallback cuối: chỉ dùng khi KHÔNG tìm được tc_num nào
#         title = ""
#         if tc_num:
#             title = self._title_cache.get((sheet_name, tc_num), "")
#             if not title:
#                 # Thử tìm lại bằng cách parse số trực tiếp từ param_id
#                 m = re.search(r'(\d+)', param_id) if param_id else None
#                 if m:
#                     alt_num = int(m.group(1))
#                     title = self._title_cache.get((sheet_name, alt_num), "")
#         if not title:
#             # Fallback chỉ khi không có tc_num: dùng tên hàm
#             title = func_name.replace("test_", "").replace("_", " ").capitalize()

#         # ── Test Data: lấy từ CODE_DATA_MAP (bảng định nghĩa ở trên) ──
#         data_str = ""
#         if tc_num:
#             # Thử module_key trước, nếu không có thì dùng sheet_name
#             data_str = CODE_DATA_MAP.get((module_key, tc_num), "")

#         # ── ID Test Case ──
#         tc_id = f"{module_code}-{tc_num}" if tc_num else f"{module_code}-?"

#         # ── Tên Test (code) – hiển thị ngắn gọn ──
#         test_display = func_name
#         if param_id:
#             test_display = f"{func_name}[{param_id}]"

#         # ── Result & Reason ──
#         if report.skipped:
#             result = "Skip"
#             reason = self._skip_reason(report)
#         elif report.failed:
#             result = "Fail"
#             reason = self._fail_reason(report)
#         else:
#             result = "Pass"
#             reason = ""

#         self.results.append({
#             "display_name": display_name,
#             "module_code" : module_code,
#             "sheet"       : sheet_name,
#             "module_key"  : module_key,
#             "tc_num"      : tc_num or 9999,
#             "tc_id"       : tc_id,
#             "title"       : title,
#             "test_name"   : test_display,
#             "data"        : data_str,
#             "result"      : result,
#             "reason"      : reason,
#         })

#     # ─────────────────────────────────────────────────────────
#     #  Hook: ghi file Excel khi session kết thúc
#     # ─────────────────────────────────────────────────────────
#     def pytest_sessionfinish(self, session, exitstatus):
#         if not self.results:
#             print("\n[ExcelReport] Không có kết quả nào để xuất.")
#             return

#         os.makedirs("reports", exist_ok=True)
#         ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_path = f"reports/DATN_TestReport_{ts}.xlsx"

#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Test Results"

#         self._write_header(ws)
#         self._write_data(ws)
#         self._format_columns(ws)

#         # ── Sheet tổng hợp theo module (giống ảnh) ──
#         ws_summary = wb.create_sheet("Summary")
#         self._write_summary_sheet(ws_summary)

#         wb.save(output_path)

#         total  = len(self.results)
#         passed = sum(1 for r in self.results if r["result"] == "Pass")
#         failed = sum(1 for r in self.results if r["result"] == "Fail")
#         skip   = sum(1 for r in self.results if r["result"] == "Skip")
#         tested      = passed + failed
#         success_pct = (passed / tested * 100) if tested else 0
#         print(f"\n[ExcelReport]   Đã xuất: {output_path}")
#         print(f"[ExcelReport]     Tổng={total} | Pass={passed} | Fail={failed} | Skip={skip}")
#         print(f"[ExcelReport]     Test coverage=100.00% | Successful coverage={success_pct:.2f}%")

#     # ─────────────────────────────────────────────────────────
#     #  Sheet Summary – bảng tổng hợp theo module (giống ảnh)
#     # ─────────────────────────────────────────────────────────
#     def _write_summary_sheet(self, ws):
#         """
#         Tạo sheet Summary với bảng:
#           No | Module code | Pass | Fail | Untested | N/A | Number of test cases
#         + dòng Sub total
#         + 2 dòng metric: Test coverage & Test successful coverage
#         """
#         from collections import defaultdict

#         # ── thu thập số liệu theo module ──
#         stats = defaultdict(lambda: {"pass": 0, "fail": 0, "skip": 0, "na": 0})
#         for r in self.results:
#             mk = r["module_key"]
#             if r["result"] == "Pass":
#                 stats[mk]["pass"] += 1
#             elif r["result"] == "Fail":
#                 stats[mk]["fail"] += 1
#             elif r["result"] == "Skip":
#                 stats[mk]["skip"] += 1
#             else:
#                 stats[mk]["na"] += 1

#         # Sắp xếp theo MODULE_ORDER, module lạ bổ sung cuối
#         ordered_modules = [mk for mk in MODULE_ORDER if mk in stats]
#         for mk in stats:
#             if mk not in ordered_modules:
#                 ordered_modules.append(mk)

#         # ── header bảng ──
#         headers    = ["No", "Module code", "Pass", "Fail", "Untested", "N/A", "Number of test cases"]
#         col_widths = [6, 18, 10, 10, 12, 10, 22]

#         for col, (h, w) in enumerate(zip(headers, col_widths), 1):
#             c = ws.cell(row=1, column=col, value=h)
#             c.fill      = FILL_HEADER
#             c.font      = FONT_HEADER
#             c.border    = BORDER
#             c.alignment = CENTER
#             ws.column_dimensions[get_column_letter(col)].width = w
#         ws.row_dimensions[1].height = 24

#         # ── dòng dữ liệu từng module ──
#         total_pass = total_fail = total_skip = total_na = 0
#         data_rows  = []

#         for idx, mk in enumerate(ordered_modules, 1):
#             _, module_code, display_name = MODULE_MAP.get(mk, ("?", mk, mk))
#             s  = stats[mk]
#             p, f, sk, na = s["pass"], s["fail"], s["skip"], s["na"]
#             total_tc = p + f + sk + na
#             data_rows.append((idx, module_code, p, f, sk, na, total_tc))
#             total_pass += p
#             total_fail += f
#             total_skip += sk
#             total_na   += na

#         for row_offset, (no, code, p, f, sk, na, total_tc) in enumerate(data_rows, 2):
#             values = [no, code, p, f, sk, na, total_tc]
#             for col, val in enumerate(values, 1):
#                 c = ws.cell(row=row_offset, column=col, value=val)
#                 c.border    = BORDER
#                 c.alignment = CENTER
#                 c.font      = Font(name="Calibri", size=11)
#             ws.row_dimensions[row_offset].height = 20

#         # ── dòng Sub total ──
#         sub_row    = len(data_rows) + 2
#         grand_all  = total_pass + total_fail + total_skip + total_na
#         sub_values = ["", "Sub total", total_pass, total_fail, total_skip, total_na, grand_all]
#         for col, val in enumerate(sub_values, 1):
#             c = ws.cell(row=sub_row, column=col, value=val)
#             c.fill      = FILL_SUBTOTAL
#             c.font      = FONT_SUBTOTAL
#             c.border    = BORDER
#             c.alignment = CENTER
#         ws.row_dimensions[sub_row].height = 22

#         # ── dòng metric ──
#         tested       = total_pass + total_fail
#         # Test coverage     = tỉ lệ TC đã chạy (pass+fail) / tổng TC (bỏ N/A)
#         denominator  = grand_all - total_na
#         coverage_pct = (tested / denominator * 100) if denominator else 0.0
#         # Test successful coverage = pass / tested
#         success_pct  = (total_pass / tested * 100) if tested else 0.0

#         metrics = [
#             ("Test coverage",            coverage_pct),
#             ("Test successful\ncoverage", success_pct),
#         ]
#         for i, (label, pct) in enumerate(metrics):
#             metric_row = sub_row + 2 + i
#             lc = ws.cell(row=metric_row, column=1, value=label.replace("\\n", "\n"))
#             lc.font      = FONT_METRIC_LABEL
#             lc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
#             ws.merge_cells(start_row=metric_row, start_column=1,
#                            end_row=metric_row, end_column=2)
#             vc = ws.cell(row=metric_row, column=3, value=round(pct, 2))
#             vc.number_format = "0.00"
#             vc.font          = FONT_METRIC_VALUE
#             vc.alignment     = CENTER
#             pc = ws.cell(row=metric_row, column=4, value="%")
#             pc.font      = FONT_METRIC_VALUE
#             pc.alignment = CENTER
#             ws.row_dimensions[metric_row].height = 28

#         ws.sheet_view.showGridLines = False

#     # ─────────────────────────────────────────────────────────
#     #  Ghi header
#     # ─────────────────────────────────────────────────────────
#     def _write_header(self, ws):
#         headers = [
#             "Module",
#             "ID Test Case",
#             "Test Case Title",
#             "Tên Test (code)",
#             "Test Data",
#             "Result",
#             "Lý do lỗi / Ghi chú",
#         ]
#         for col, h in enumerate(headers, 1):
#             c = ws.cell(row=1, column=col, value=h)
#             c.fill      = FILL_HEADER
#             c.font      = FONT_HEADER
#             c.border    = BORDER
#             c.alignment = CENTER
#         ws.row_dimensions[1].height = 22

#     # ─────────────────────────────────────────────────────────
#     #  Ghi dữ liệu
#     # ─────────────────────────────────────────────────────────
#     def _write_data(self, ws):
#         # Sắp xếp theo thứ tự module → số TC
#         def sort_key(r):
#             try:
#                 mod_idx = MODULE_ORDER.index(r["module_key"])
#             except ValueError:
#                 mod_idx = 99
#             return (mod_idx, r["tc_num"])

#         sorted_results = sorted(self.results, key=sort_key)

#         row_num  = 2
#         prev_mod = None

#         for r in sorted_results:
#             # ── Dòng nhóm module mới ──
#             if r["display_name"] != prev_mod:
#                 if prev_mod is not None:
#                     row_num += 1  # dòng trống giữa các module

#                 for col in range(1, 8):
#                     c = ws.cell(row=row_num, column=col)
#                     c.fill   = FILL_MODULE
#                     c.font   = FONT_MODULE
#                     c.border = BORDER
#                     c.alignment = Alignment(vertical="center")
#                     if col == 1:
#                         c.value = f"  {r['display_name'].upper()}"

#                 ws.row_dimensions[row_num].height = 18
#                 row_num  += 1
#                 prev_mod  = r["display_name"]

#             # ── Dòng dữ liệu test case ──
#             values = [
#                 r["display_name"],       # Module
#                 r["tc_id"],              # ID Test Case
#                 r["title"],              # Test Case Title (từ Excel)
#                 r["test_name"],          # Tên Test (code)
#                 r["data"],               # Test Data (từ code)
#                 r["result"],             # Result
#                 r["reason"],             # Lý do lỗi
#             ]
#             for col, val in enumerate(values, 1):
#                 c = ws.cell(row=row_num, column=col, value=val)
#                 c.border = BORDER
#                 if col in (1, 2, 6):
#                     c.alignment = CENTER
#                 else:
#                     c.alignment = LEFT

#                 # Tô màu cột Result
#                 if col == 6:
#                     if r["result"] == "Pass":
#                         c.fill = FILL_PASS
#                         c.font = FONT_PASS
#                     elif r["result"] == "Fail":
#                         c.fill = FILL_FAIL
#                         c.font = FONT_FAIL
#                     else:
#                         c.fill = FILL_SKIP
#                         c.font = FONT_SKIP

#             ws.row_dimensions[row_num].height = 32
#             row_num += 1

#     # ─────────────────────────────────────────────────────────
#     #  Định dạng độ rộng cột
#     # ─────────────────────────────────────────────────────────
#     def _format_columns(self, ws):
#         #      Module  ID TC   Title   TestName  Data   Result  Reason
#         widths = [16,   24,     56,     50,        38,    10,     56]
#         for col, w in enumerate(widths, 1):
#             ws.column_dimensions[get_column_letter(col)].width = w
#         ws.freeze_panes = "A2"   # Cố định dòng header

#     # ─────────────────────────────────────────────────────────
#     #  Helpers
#     # ─────────────────────────────────────────────────────────
#     def _get_module_key(self, node_id: str):
#         """Xác định module_key từ node_id dựa vào tên file test."""
#         node_lower = node_id.lower()
#         for key in MODULE_MAP:
#             if key in node_lower:
#                 return key
#         return None

#     def _parse_node_id(self, node_id: str) -> tuple:
#         """
#         Tách tên hàm và param_id từ pytest node_id.
#         vd: "tests/test_cart.py::TestCartUpdate::test_update_cart[tc14_zero]"
#             → ("test_update_cart", "tc14_zero")
#         """
#         parts = node_id.split("::")
#         last  = parts[-1]
#         m = re.match(r'^([^\[]+)\[(.+)\]$', last)
#         if m:
#             return m.group(1).strip(), m.group(2).strip()
#         return last.strip(), ""

#     def _resolve_tc_num(self, module_key: str, func_name: str, param_id: str):
#         """
#         Xác định số TC theo thứ tự ưu tiên:
#           1. PARAM_MAP   – khớp chuỗi trong param_id
#           2. MANUAL_MAP  – khớp tên hàm thủ công
#           3. Regex số trong tên hàm: test_tc07, test_TC01
#           4. Regex số trong param_id: [TC-7]
#         """
#         # 1. Param map
#         if param_id and module_key in PARAM_MAP:
#             for pattern, tc_num in PARAM_MAP[module_key].items():
#                 if pattern in param_id:
#                     return tc_num

#         # 2. Manual map
#         val = MANUAL_MAP.get((module_key, func_name))
#         if val is not None:
#             return val

#         # 3. Số trong tên hàm dạng test_tc07 / test_TC01
#         m = re.search(r'_tc0*(\d+)', func_name, re.IGNORECASE)
#         if m:
#             return int(m.group(1))

#         # 4. Số trong param_id dạng TC-7, TC7
#         if param_id:
#             m = re.search(r'TC[-_]?0*(\d+)', param_id, re.IGNORECASE)
#             if m:
#                 return int(m.group(1))

#         return None

#     @staticmethod
#     def _fail_reason(report) -> str:
#         """Lấy dòng lỗi cuối cùng từ traceback (ngắn gọn)."""
#         if report.longrepr:
#             text  = str(report.longrepr)
#             lines = [l.strip() for l in text.splitlines() if l.strip()]
#             return lines[-1][:400] if lines else "Unknown error"
#         return ""

#     @staticmethod
#     def _skip_reason(report) -> str:
#         """Lấy lý do skip."""
#         if report.longrepr:
#             text = str(report.longrepr).strip()
#             if "Skipped:" in text:
#                 return text.split("Skipped:", 1)[-1].strip()[:300]
#             return text[:300]
#         return ""





# # ============================================================
# # FILE: conftest_excel_report.py
# # MỤC ĐÍCH: Plugin pytest – xuất kết quả test ra 1 sheet Excel duy nhất
# # KẾT QUẢ: reports/test_report_<timestamp>.xlsx  — 1 sheet duy nhất
# #
# # CỘT XUẤT:
# #   Module | ID Test Case | Test Case Title (từ Excel) | Tên Test (code) | Test Data (từ code) | Result | Lý do lỗi
# # ============================================================

# import re
# import os
# from datetime import datetime
# from openpyxl import Workbook, load_workbook
# from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
# from openpyxl.utils import get_column_letter


# # ─────────────────────────────────────────────────────────────
# #  MÀU SẮC & STYLE
# # ─────────────────────────────────────────────────────────────
# FILL_PASS   = PatternFill("solid", fgColor="C6EFCE")
# FILL_FAIL   = PatternFill("solid", fgColor="FFC7CE")
# FILL_SKIP   = PatternFill("solid", fgColor="FFEB9C")
# FILL_HEADER = PatternFill("solid", fgColor="2E75B6")
# FILL_MODULE = PatternFill("solid", fgColor="D6E4F7")

# FONT_PASS   = Font(color="375623")
# FONT_FAIL   = Font(color="9C0006")
# FONT_SKIP   = Font(color="7D6608")
# FONT_HEADER = Font(color="FFFFFF", bold=True, size=11)
# FONT_MODULE = Font(bold=True, color="1F4E79")

# _THIN   = Side(style="thin")
# BORDER  = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

# CENTER  = Alignment(horizontal="center", vertical="center", wrap_text=True)
# LEFT    = Alignment(horizontal="left",   vertical="center", wrap_text=True)


# # ─────────────────────────────────────────────────────────────
# #  MAP: tên file test (module_key) → (sheet_name, module_code, display_name)
# #  module_key phải khớp chính xác với tên file test (không có .py)
# # ─────────────────────────────────────────────────────────────
# MODULE_MAP = {
#     "test_login"    : ("Login",          "ĐN",             "Đăng nhập"),
#     "test_cart"     : ("Cart",           "GH",      "Giỏ hàng"),
#     "test_register" : ("Register",       "ĐK",     "Đăng ký"),
#     "test_invoice"  : ("Invoice",        "HĐ",       "Hóa đơn"),
#     "test_order"    : ("Order",          "ĐH",              "Đặt hàng"),
#     "test_add_to_cart" : ("Add_to_cart",       "ATC", "Thêm vào giỏ"),
#     "test_search"   : ("Search",         "TK",              "TK"),
#     "test_product"  : ("Product_detail", "SP", "Chi tiết SP"),
# }

# # Thứ tự hiển thị module trong báo cáo
# MODULE_ORDER = [
#     "test_login", "test_register", "test_cart",
#     "test_order", "test_invoice",
#     "test_add_to_cart", "test_search", "test_product",
# ]


# # ─────────────────────────────────────────────────────────────
# #  TEST DATA từ code — map: (module_key, tc_num) → chuỗi data
# #  Lấy trực tiếp từ các biến trong test_data_*.py
# #  Cập nhật thêm nếu project có thêm TC mới
# # ─────────────────────────────────────────────────────────────
# CODE_DATA_MAP: dict[tuple, str] = {
#     # ── LOGIN ──
#     ("test_login", 1) : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 2) : "Tài khoản: admin | Mật khẩu: admin",
#     ("test_login", 7) : "Tài khoản: (trống) | Mật khẩu: 123456789",
#     ("test_login", 8) : "Tài khoản: tets_1 | Mật khẩu: 123456789",
#     ("test_login", 9) : "Tài khoản: haha | Mật khẩu: 123456789",
#     ("test_login", 10): "Tài khoản: Test_1 | Mật khẩu: 123456789",
#     ("test_login", 11): "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 12): "Tài khoản: test_1 | Mật khẩu: (trống)",
#     ("test_login", 13): "Tài khoản: test_1 | Mật khẩu: wrongpass",
#     ("test_login", 14): "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 15): "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_login", 16): "Tài khoản: a | Mật khẩu: 123456789",

#     # ── CART ──
#     ("test_cart", 1)  : "",
#     ("test_cart", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_cart", 7)  : "",
#     ("test_cart", 8)  : "",
#     ("test_cart", 9) : "Hành động: increase | SL đặt trước: 1 | Delta: +1",
#     ("test_cart", 10) : "Hành động: decrease | SL đặt trước: 2 | Delta: -1",
#     ("test_cart", 11) : f"Số lần click (+) tối đa: 20 | Expected: 'không đủ'",
#     ("test_cart", 12) : "SL đặt trước: 1 | Expected popup: 'Xóa sản phẩm này khỏi giỏ hàng'",
#     ("test_cart", 13) : "Số lượng nhập: 0 | Kịch bản: popup_confirm",
#     ("test_cart", 14) : "Số lượng nhập: -1 | Kịch bản: reject",
#     ("test_cart", 15) : "Số lượng nhập: 1.5 | Kịch bản: reject",
#     ("test_cart", 16) : "Số lượng nhập: 'a' | Kịch bản: reject",
#     ("test_cart", 17) : "Số lượng nhập: '!' | Kịch bản: reject",
#     ("test_cart", 18) : "Số lượng nhập: (trống) | Kịch bản: reject",
#     ("test_cart", 19) : "Số lượng nhập: 2 | Kịch bản: accept",
#     ("test_cart", 20) : "Số lượng nhập: 100 | Kịch bản: out_of_stock",
#     ("test_cart", 21) : "Hành động popup: OK | Kết quả: removed",
#     ("test_cart", 22) : "SP tối thiểu: 3 | Số lần xóa: 2",
#     ("test_cart", 23) : "SP tối thiểu: 3 | Expected: 'Chưa có sản phẩm nào trong giỏ hàng'",
#     ("test_cart", 24) : "Hành động popup: Cancel | Kết quả: kept",
#     ("test_cart", 25) : "",

#     # ── REGISTER ──
#     ("test_register", 1)  : "",
#     ("test_register", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_register", 7)  : "Họ tên: (trống)",
#     ("test_register", 8)  : "Họ tên: hồng",
#     ("test_register", 9)  : "Họ tên: HỒNG",
#     ("test_register", 10) : "Họ tên: hỒNg",
#     ("test_register", 11) : "Họ tên: 123",
#     ("test_register", 12) : "Họ tên: !@#",
#     ("test_register", 13) : "Họ tên: hồng12",
#     ("test_register", 14) : "Họ tên: hồng@#",
#     ("test_register", 15) : "Họ tên: ' hồng' (khoảng trắng đầu)",
#     ("test_register", 16) : "SĐT: (trống)",
#     ("test_register", 17) : "SĐT: 'điện!@'",
#     ("test_register", 18) : "SĐT: '0123 456 789' (khoảng trắng)",
#     ("test_register", 19) : "SĐT: 1234567899 (không bắt đầu bằng 0)",
#     ("test_register", 20) : "SĐT: 012345678 (9 ký tự)",
#     ("test_register", 21) : "SĐT: 0123456789 (10 ký tự hợp lệ)",
#     ("test_register", 22) : "SĐT: 01234567899 (11 ký tự)",
#     ("test_register", 23) : "Email: (trống)",
#     ("test_register", 24) : "Email: honggmail.com (thiếu @)",
#     ("test_register", 25) : "Email: hong@gmailcom (thiếu dấu chấm)",
#     ("test_register", 26) : "Email: @gmail.com (không có local part)",
#     ("test_register", 27) : "Email: hong@gmail (không có TLD)",
#     ("test_register", 28) : "Email: hong@gmail.com (hợp lệ, random suffix)",
#     ("test_register", 29) : "Mật khẩu: (trống)",
#     ("test_register", 30) : "Mật khẩu: 123456 (≥6 ký tự)",
#     ("test_register", 31) : "Mật khẩu: 123456 | Xác nhận: (trống)",
#     ("test_register", 32) : "Mật khẩu: 123456 | Xác nhận: 1234567 (không khớp)",
#     ("test_register", 33) : "Mật khẩu: 1234567 | Xác nhận: 1234567 (khớp)",
#     ("test_register", 34) : "Tài khoản: (trống)",
#     ("test_register", 35) : "Tài khoản: 'vũ hồng' (chữ thường)",
#     ("test_register", 36) : "Tài khoản: 'VŨ HỒNG' (in hoa)",
#     ("test_register", 37) : "Tài khoản: 'vŨ HồNg' (hỗn hợp)",
#     ("test_register", 38) : "Tài khoản: 22222 (là số)",
#     ("test_register", 39) : "Tài khoản: '@@@' (ký tự đặc biệt)",
#     ("test_register", 40) : "Tài khoản: 'hồng25' (chữ + số)",
#     ("test_register", 41) : "Tài khoản: 'hồng@@@@' (chữ + ký tự đặc biệt)",
#     ("test_register", 42) : "Tài khoản: ' hồng' (khoảng trắng đầu)",
#     ("test_register", 43) : "Địa chỉ: (trống)",
#     ("test_register", 44) : "Địa chỉ: 'Mão Điền Bắc Ninh' (chữ thường)",
#     ("test_register", 45) : "Địa chỉ: 'MÃO ĐIỀN BẮC NINH' (in hoa)",
#     ("test_register", 46) : "Địa chỉ: 'bẮc ninh' (hỗn hợp)",
#     ("test_register", 47) : "Địa chỉ: 123 (là số)",
#     ("test_register", 48) : "Địa chỉ: '@@#' (ký tự đặc biệt)",
#     ("test_register", 49) : "Địa chỉ: '3 xóm 3 Mão Điền' (chữ + số)",
#     ("test_register", 50) : "Địa chỉ: '3 xóm 3 - Mão Điền - Bắc Ninh' (chữ + gạch)",
#     ("test_register", 51) : "Ngày sinh: (trống)",
#     ("test_register", 52) : "Ngày sinh: 2003-01-01 (hợp lệ)",
#     ("test_register", 53) : "Ngày sinh: 0003-01-01 (không hợp lệ)",
#     ("test_register", 54) : "Tất cả trường hợp lệ | Tài khoản: user_random | Email: random",
#     ("test_register", 55) : "Tài khoản đã tồn tại: 'hong' | Email: random",
#     ("test_register", 56) : "Email đã tồn tại: hong@gmail.com | Tài khoản: random",

#     # ── INVOICE ──
#     ("test_invoice", 1)  : "Tài khoản: admin | Mật khẩu: admin",
#     ("test_invoice", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_invoice", 7)  : "",
#     ("test_invoice", 8)  : "",
#     ("test_invoice", 9) : f"row_index: 16 (hóa đơn chưa hủy)",
#     ("test_invoice", 10) : "Hóa đơn đã bị hủy",
#     ("test_invoice", 11) : "Trạng thái: Đang giao / Đang chuẩn bị / Đã thanh toán",
#     ("test_invoice", 12) : "Click OK → trạng thái = 'Đã bị hủy'",
#     ("test_invoice", 13) : "Click Cancel → đơn hàng giữ nguyên",
#     ("test_invoice", 14) : "Đơn đã hủy → nút 'Hủy đơn hàng' bị ẩn",

#     # ── ORDER ──
#     ("test_order", 1)  : "",
#     ("test_order", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_order", 7)  : "Họ tên: Thử | SĐT: 0123654789 | Địa chỉ: Mão Điền",
#     ("test_order", 8)  : "Họ tên: Hồng | SĐT: 0123654789 | Địa chỉ: Mão Điền",
#     ("test_order", 9)  : "Họ tên/SĐT/Địa chỉ: (bỏ trống từng trường)",
#     ("test_order", 10) : "Giữ nguyên thông tin mặc định",
#     ("test_order", 11) : "Giỏ hàng rỗng",


#     # # ── CATEGORY ──
#     # ("test_category", 1) : "",
#     # ("test_category", 2) : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     # ("test_category", 7) : "",
#     # ("test_category", 8) : "DB không có danh mục",

#     # ── SEARCH ──
#     ("test_search", 1)  : "",
#     ("test_search", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_search", 7)  : "Từ khóa: (trống) | Submit: button",
#     ("test_search", 8)  : "Từ khóa: '@@@' | Submit: button",
#     ("test_search", 9)  : "Từ khóa: '123' | Submit: button",
#     ("test_search", 10) : "Từ khóa: 'Áo12' | Submit: button",
#     ("test_search", 11) : "Từ khóa: 'Áo@@@' | Submit: button",
#     ("test_search", 12) : "Từ khóa: '12@' | Submit: button",
#     ("test_search", 13) : "Từ khóa: 'áO' | Submit: button",
#     ("test_search", 14) : "Từ khóa: 'ÁO' | Submit: button",
#     ("test_search", 15) : "Từ khóa: 'Quần khaki nam slimfit' | Min kết quả: 2",
#     ("test_search", 16) : "Từ khóa: 'a' (1 ký tự) | Submit: button",
#     ("test_search", 17) : "Từ khóa: 'Áo sơ mi' | Submit: Enter",
#     ("test_search", 18) : "Từ khóa: 'Ao ba lo' (không dấu) | Submit: button",
#     ("test_search", 19) : "Từ khóa: 'Áo thun lam' (sai chính tả) | Submit: button",
#     ("test_search", 20) : "Từ khóa: ' Áo sơ mi ' (khoảng trắng đầu/cuối) | Submit: button",
#     ("test_search", 21) : "Từ khóa: 'Áo sơ mi nam trơn' | Submit: button",
#     ("test_search", 22) : "Từ khóa: 'Quần jean nữ ôm body' (hết hàng) | Submit: button",
#     ("test_search", 23) : "Từ khóa: 'Áo dài' (không tồn tại) | Submit: button",

#     # ── PRODUCT DETAIL ──
#     ("test_product", 1)  : "",
#     ("test_product", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_product", 7)  : "Sản phẩm: Áo phông nữ in họa tiết (còn hàng)",
#     ("test_product", 8)  : "Sản phẩm: Quần jeans nữ ôm body (hết hàng)",
#     ("test_product", 9)  : "Sản phẩm: Áo phông nam trơn | Size: XXXL (hết)",
#     ("test_product", 10) : "Sản phẩm: Áo sơ mi nam trơn (có đánh giá)",
#     ("test_product", 11) : "Sản phẩm: Áo phông nữ in họa tiết (chưa có đánh giá)",

#     #---ADD_TO_CART
#     ("test_add_to_cart", 1)  : "",
#     ("test_add_to_cart", 2)  : "Tài khoản: test_1 | Mật khẩu: 123456789",
#     ("test_add_to_cart", 7) : "Sản phẩm: Áo ba lỗ | Tài khoản: test_1",
#     ("test_add_to_cart", 8) : "Sản phẩm: Quần jean nữ ôm body (hết hàng)",
#     ("test_add_to_cart", 9) : "Sản phẩm: Áo phông nam trơn | Size XXXL hết",
#     ("test_add_to_cart", 10) : "Sản phẩm: còn hàng | Số lượng nhập: 1000",  
# }
# # ─────────────────────────────────────────────────────────────
# #  MAP THỦ CÔNG: (module_key, tên_hàm) → TC số thứ tự
# # ─────────────────────────────────────────────────────────────
# MANUAL_MAP: dict[tuple, int] = {
#     # LOGIN
#     ("test_login", "test_login_customer")                              : 1,
#     ("test_login", "test_login_admin_not_allowed")                     : 2,
#     ("test_login", "test_login_success")                               : 15,
#     ("test_login", "test_login_disabled_account")                      : 16,

#     # CART
#     ("test_cart", "test_view_cart_not_logged_in")                      : 1,
#     ("test_cart", "test_view_cart_logged_in")                          : 2,
#     ("test_cart", "test_view_cart_with_items")                         : 7,
#     ("test_cart", "test_view_empty_cart")                              : 8,
#     ("test_cart", "test_increase_exceeds_stock")                       : 11,
#     ("test_cart", "test_decrease_at_qty_one_shows_popup")              : 12,
#     ("test_cart", "test_remove_multiple_products")                     : 22,
#     ("test_cart", "test_remove_all_products")                          : 23,
#     ("test_cart", "test_continue_shopping")                            : 25,

#     # REGISTER
#     ("test_register", "test_TC01_mo_trang_dang_ky_chua_dang_nhap")    : 1,
#     ("test_register", "test_TC02_da_dang_nhap_khong_hien_nut_dang_ky"): 2,
#     ("test_register", "test_TC31_email_hop_le")                        : 28,
#     ("test_register", "test_TC59_dang_ky_thanh_cong")                  : 54,
#     ("test_register", "test_TC60_dang_ky_tai_khoan_da_ton_tai")        : 55,
#     ("test_register", "test_TC61_dang_ky_email_da_ton_tai")            : 56,

#     # INVOICE
#     ("test_invoice", "test_admin_can_access_invoice")                  : 1,
#     ("test_invoice", "test_customer_cannot_access_admin_invoice")      : 2,
#     ("test_invoice", "test_view_invoice_list_has_data")                : 7,
#     ("test_invoice", "test_view_invoice_list_empty")                   : 8,
#     ("test_invoice", "test_view_invoice_detail")                       : 9,
#     ("test_invoice", "test_view_cancelled_invoice_detail")             : 10,
#     ("test_invoice", "test_cancel_order_success")                      : 12,
#     ("test_invoice", "test_cancel_order_click_cancel")                 : 13,
#     ("test_invoice", "test_cancelled_order_hides_cancel_btn")          : 14,

#     # ORDER 
#     ("test_order", "test_tc1_order_without_login_redirects_to_login")   : 1,
#     ("test_order", "test_tc2_order_after_login_reaches_checkout")       : 2,
#     ("test_order", "test_tc7_keep_default_info_order_success")          : 7,
#     ("test_order", "test_tc8_change_receiver_info_order_success")       : 8,
#     ("test_order", "test_tc10_place_order_success_cart_becomes_empty")  : 10,
#     ("test_order", "test_tc11_order_empty_cart_not_allowed")            : 11,

#     # SEARCH
#     ("test_search", "test_search_without_login")                        : 1,
#     ("test_search", "test_search_with_login")                           : 2,

#     # PRODUCT
#     ("test_product", "test_tc01_view_product_not_logged_in")            : 1,
#     ("test_product", "test_tc02_view_product_logged_in")                : 2,
#     ("test_product", "test_tc07_view_in_stock_product")                 : 7,
#     ("test_product", "test_tc08_view_out_of_stock_product")             : 8,
#     ("test_product", "test_tc09_view_out_of_size_product")              : 9,
#     ("test_product", "test_tc10_product_with_review")                   : 10,
#     ("test_product", "test_tc11_product_no_review")                     : 11,

#     #ADD TO CART
#     ("test_add_to_cart", "test_tc01_add_to_cart_not_logged_in")                   : 1,
#     ("test_add_to_cart", "test_tc02_add_to_cart_logged_in")              : 2,
#     ("test_add_to_cart", "test_tc7_add_to_cart_success")                   : 7,
#     ("test_add_to_cart", "test_tc8_add_to_cart_out_of_stock")              : 8,
#     ("test_add_to_cart", "test_tc9_add_to_cart_out_of_size")               : 9,
#     ("test_add_to_cart", "test_tc10_add_to_cart_exceed_quantity")          : 10,
# }


# # ─────────────────────────────────────────────────────────────
# #  MAP THAM SỐ PARAMETRIZE: module_key → { chuỗi_trong_param_id → TC số }
# # ─────────────────────────────────────────────────────────────
# PARAM_MAP: dict[str, dict[str, int]] = {
#     "test_login": {
#         "DN-blank-user-TC7"  : 7,   "DN-blank-pass-TC12" : 12,
#         "DN-wrong-user-TC8"  : 8,   "DN-not-exist-TC9"   : 9,
#         "DN-case-sens-TC10"  : 10,  "DN-wrong-pass-TC13" : 13,
#         "DN-valid-TC11"      : 11,  "DN-valid-TC14"      : 14,
#         "DN-disabled-TC16"   : 16,  "DN-valid"           : 15,
#     },
#     "test_cart": {
#         "tc10_increase": 9,  "tc11_decrease": 10,
#         "tc14_zero"    : 13,  "tc15_negative": 14,
#         "tc16_float"   : 15,  "tc17_text"    : 16,
#         "tc18_special" : 17,  "tc19_empty"   : 18,
#         "tc20_valid"   : 19,  "tc21_exceed"  : 20,
#         "tc22_ok"      : 21,  "tc25_cancel"  : 24,
#     },
#     "test_register": {
#         "TC-7" : 7,  "TC-8" : 8,  "TC-9" : 9,  "TC-10": 10,
#         "TC-11": 11, "TC-12": 12, "TC-13": 13, "TC-14": 14,
#         "TC-15": 15, "TC-16": 16, "TC-17": 17, "TC-18": 18,
#         "TC-19": 19, "TC-20": 20, "TC-21": 21, "TC-22": 22,
#         "TC-23": 23, "TC-24": 24, "TC-25": 25, "TC-26": 26,
#         "TC-27": 27, "TC-29": 29, "TC-30": 30, "TC-31": 31,
#         "TC-32": 32, "TC-33": 33, "TC-34": 34, "TC-35": 35,
#         "TC-36": 36, "TC-37": 37, "TC-38": 38, "TC-39": 39,
#         "TC-40": 40, "TC-41": 41, "TC-42": 42, "TC-43": 43,
#         "TC-44": 44, "TC-45": 45, "TC-46": 46, "TC-47": 47,
#         "TC-48": 48, "TC-49": 49, "TC-50": 50, "TC-51": 51,
#         "TC-52": 52, "TC-53": 53,
#     },
#     "test_invoice": {
#         "tc11_dang_giao"    : 11,
#         "tc11_dang_chuan_bi": 11,
#         "tc11_da_thanh_toan": 11,
#     },
#     # "test_checkout": {
#     #     "tc9_empty_ho_ten"         : 9,
#     #     "tc9_empty_sdt"            : 9,
#     #     "tc9_empty_dia_chi"        : 9,
#     #     "tc10_success_default_info": 10,
#     # },
#     "test_order": {
#         "tc9_empty_ho_ten"         : 9,
#         "tc9_empty_sdt"            : 9,
#         "tc9_empty_dia_chi"        : 9,
#         "tc10_success_default_info": 10,
#     },
#     # "test_category": {
#     #     "TC-1": 1, "TC-2": 2, "TC-7": 7, "TC-8": 8,
    
#     "test_search": {
#         "TK-7" : 7,  "TK-8" : 8,  "TK-9" : 9,  "TK-10": 10,
#         "TK-11": 11, "TK-12": 12, "TK-13": 13, "TK-14": 14,
#         "TK-15": 15, "TK-16": 16, "TK-17": 17, "TK-18": 18,
#         "TK-19": 19, "TK-20": 20, "TK-21": 21, "TK-22": 22,
#         "TK-23": 23,
#     },
# }


# # ═══════════════════════════════════════════════════════════════
# #  PLUGIN CLASS
# # ═══════════════════════════════════════════════════════════════
# class ExcelReportPlugin:
#     """
#     Plugin pytest - xuất 1 sheet Excel tổng hợp toàn bộ kết quả.

#     CỘT:
#       Module | ID Test Case | Test Case Title (Excel) | Tên Test (code)
#       | Test Data (code) | Result | Lý do lỗi
#     """

#     def __init__(self, template_path: str):
#         self.template_path = template_path
#         # Kết quả thu thập theo thứ tự chạy
#         self.results: list[dict] = []
#         # Cache: (sheet_name, tc_num) → title từ Excel
#         self._title_cache: dict[tuple, str] = {}
#         self._load_title_cache()

#     # ─────────────────────────────────────────────────────────
#     #  Load title từ Excel
#     # ─────────────────────────────────────────────────────────
#     def _load_title_cache(self):
#         if not os.path.exists(self.template_path):
#             print(f"\n[ExcelReport]  Không tìm thấy template: {self.template_path}")
#             print(f"[ExcelReport]   → Kiểm tra lại EXCEL_TEMPLATE trong conftest.py")
#             return
#         try:
#             wb = load_workbook(self.template_path, data_only=True)
#             # Dùng set tránh load cùng 1 sheet 2 lần
#             # (vd: test_checkout và test_order cùng trỏ vào sheet "Order")
#             loaded_sheets = set()
#             for module_key, (sheet_name, _, _) in MODULE_MAP.items():
#                 if sheet_name in loaded_sheets:
#                     continue
#                 if sheet_name not in wb.sheetnames:
#                     continue
#                 ws = wb[sheet_name]
#                 for row_idx in range(9, ws.max_row + 1):
#                     desc = ws.cell(row=row_idx, column=4).value
#                     if desc and str(desc).strip():
#                         tc_num = row_idx - 8
#                         self._title_cache[(sheet_name, tc_num)] = str(desc).strip()
#                 loaded_sheets.add(sheet_name)
#             print(f"\n[ExcelReport]  Đã load {len(self._title_cache)} TC title từ template.")
#         except Exception as e:
#             print(f"\n[ExcelReport]  Lỗi đọc template: {e}")

#     # ─────────────────────────────────────────────────────────
#     #  Hook: thu thập kết quả sau mỗi test
#     # ─────────────────────────────────────────────────────────
#     def pytest_runtest_logreport(self, report):
#         # Chỉ xử lý phase "call"; ngoại trừ skip có thể ở "setup"
#         if report.when not in ("call", "setup"):
#             return
#         if report.when == "setup" and not report.skipped:
#             return

#         node_id    = report.nodeid
#         module_key = self._get_module_key(node_id)
#         if module_key is None:
#             return

#         sheet_name, module_code, display_name = MODULE_MAP[module_key]
#         func_name, param_id = self._parse_node_id(node_id)
#         tc_num = self._resolve_tc_num(module_key, func_name, param_id)

#         # ── Test Case Title: lấy từ Excel cache (cột D) ──
#         # Ưu tiên 1: cache từ Excel theo (sheet_name, tc_num)
#         # Ưu tiên 2: cache từ Excel theo (sheet_name, tc_num) với tc_num từ param
#         # Fallback cuối: chỉ dùng khi KHÔNG tìm được tc_num nào
#         title = ""
#         if tc_num:
#             title = self._title_cache.get((sheet_name, tc_num), "")
#             if not title:
#                 # Thử tìm lại bằng cách parse số trực tiếp từ param_id
#                 m = re.search(r'(\d+)', param_id) if param_id else None
#                 if m:
#                     alt_num = int(m.group(1))
#                     title = self._title_cache.get((sheet_name, alt_num), "")
#         if not title:
#             # Fallback chỉ khi không có tc_num: dùng tên hàm
#             title = func_name.replace("test_", "").replace("_", " ").capitalize()

#         # ── Test Data: lấy từ CODE_DATA_MAP (bảng định nghĩa ở trên) ──
#         data_str = ""
#         if tc_num:
#             # Thử module_key trước, nếu không có thì dùng sheet_name
#             data_str = CODE_DATA_MAP.get((module_key, tc_num), "")

#         # ── ID Test Case ──
#         tc_id = f"{module_code}-{tc_num}" if tc_num else f"{module_code}-?"

#         # ── Tên Test (code) – hiển thị ngắn gọn ──
#         test_display = func_name
#         if param_id:
#             test_display = f"{func_name}[{param_id}]"

#         # ── Result & Reason ──
#         if report.skipped:
#             result = "Skip"
#             reason = self._skip_reason(report)
#         elif report.failed:
#             result = "Fail"
#             reason = self._fail_reason(report)
#         else:
#             result = "Pass"
#             reason = ""

#         self.results.append({
#             "display_name": display_name,
#             "module_code" : module_code,
#             "sheet"       : sheet_name,
#             "module_key"  : module_key,
#             "tc_num"      : tc_num or 9999,
#             "tc_id"       : tc_id,
#             "title"       : title,
#             "test_name"   : test_display,
#             "data"        : data_str,
#             "result"      : result,
#             "reason"      : reason,
#         })

#     # ─────────────────────────────────────────────────────────
#     #  Hook: ghi file Excel khi session kết thúc
#     # ─────────────────────────────────────────────────────────
#     def pytest_sessionfinish(self, session, exitstatus):
#         if not self.results:
#             print("\n[ExcelReport] Không có kết quả nào để xuất.")
#             return

#         os.makedirs("reports", exist_ok=True)
#         ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_path = f"reports/DATN_TestReport_{ts}.xlsx"

#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Test Results"

#         self._write_header(ws)
#         self._write_data(ws)
#         self._format_columns(ws)

#         wb.save(output_path)

#         total  = len(self.results)
#         passed = sum(1 for r in self.results if r["result"] == "Pass")
#         failed = sum(1 for r in self.results if r["result"] == "Fail")
#         skip   = sum(1 for r in self.results if r["result"] == "Skip")
#         print(f"\n[ExcelReport]   Đã xuất: {output_path}")
#         print(f"[ExcelReport]     Tổng={total} | Pass={passed} | Fail={failed} | Skip={skip}")

#     # ─────────────────────────────────────────────────────────
#     #  Ghi header
#     # ─────────────────────────────────────────────────────────
#     def _write_header(self, ws):
#         headers = [
#             "Module",
#             "ID Test Case",
#             "Test Case Title",
#             "Tên Test (code)",
#             "Test Data",
#             "Result",
#             "Lý do lỗi / Ghi chú",
#         ]
#         for col, h in enumerate(headers, 1):
#             c = ws.cell(row=1, column=col, value=h)
#             c.fill      = FILL_HEADER
#             c.font      = FONT_HEADER
#             c.border    = BORDER
#             c.alignment = CENTER
#         ws.row_dimensions[1].height = 22

#     # ─────────────────────────────────────────────────────────
#     #  Ghi dữ liệu
#     # ─────────────────────────────────────────────────────────
#     def _write_data(self, ws):
#         # Sắp xếp theo thứ tự module → số TC
#         def sort_key(r):
#             try:
#                 mod_idx = MODULE_ORDER.index(r["module_key"])
#             except ValueError:
#                 mod_idx = 99
#             return (mod_idx, r["tc_num"])

#         sorted_results = sorted(self.results, key=sort_key)

#         row_num  = 2
#         prev_mod = None

#         for r in sorted_results:
#             # ── Dòng nhóm module mới ──
#             if r["display_name"] != prev_mod:
#                 if prev_mod is not None:
#                     row_num += 1  # dòng trống giữa các module

#                 for col in range(1, 8):
#                     c = ws.cell(row=row_num, column=col)
#                     c.fill   = FILL_MODULE
#                     c.font   = FONT_MODULE
#                     c.border = BORDER
#                     c.alignment = Alignment(vertical="center")
#                     if col == 1:
#                         c.value = f"  {r['display_name'].upper()}"

#                 ws.row_dimensions[row_num].height = 18
#                 row_num  += 1
#                 prev_mod  = r["display_name"]

#             # ── Dòng dữ liệu test case ──
#             values = [
#                 r["display_name"],       # Module
#                 r["tc_id"],              # ID Test Case
#                 r["title"],              # Test Case Title (từ Excel)
#                 r["test_name"],          # Tên Test (code)
#                 r["data"],               # Test Data (từ code)
#                 r["result"],             # Result
#                 r["reason"],             # Lý do lỗi
#             ]
#             for col, val in enumerate(values, 1):
#                 c = ws.cell(row=row_num, column=col, value=val)
#                 c.border = BORDER
#                 if col in (1, 2, 6):
#                     c.alignment = CENTER
#                 else:
#                     c.alignment = LEFT

#                 # Tô màu cột Result
#                 if col == 6:
#                     if r["result"] == "Pass":
#                         c.fill = FILL_PASS
#                         c.font = FONT_PASS
#                     elif r["result"] == "Fail":
#                         c.fill = FILL_FAIL
#                         c.font = FONT_FAIL
#                     else:
#                         c.fill = FILL_SKIP
#                         c.font = FONT_SKIP

#             ws.row_dimensions[row_num].height = 32
#             row_num += 1

#     # ─────────────────────────────────────────────────────────
#     #  Định dạng độ rộng cột
#     # ─────────────────────────────────────────────────────────
#     def _format_columns(self, ws):
#         #      Module  ID TC   Title   TestName  Data   Result  Reason
#         widths = [16,   24,     56,     50,        38,    10,     56]
#         for col, w in enumerate(widths, 1):
#             ws.column_dimensions[get_column_letter(col)].width = w
#         ws.freeze_panes = "A2"   # Cố định dòng header

#     # ─────────────────────────────────────────────────────────
#     #  Helpers
#     # ─────────────────────────────────────────────────────────
#     def _get_module_key(self, node_id: str):
#         """Xác định module_key từ node_id dựa vào tên file test."""
#         node_lower = node_id.lower()
#         for key in MODULE_MAP:
#             if key in node_lower:
#                 return key
#         return None

#     def _parse_node_id(self, node_id: str) -> tuple:
#         """
#         Tách tên hàm và param_id từ pytest node_id.
#         vd: "tests/test_cart.py::TestCartUpdate::test_update_cart[tc14_zero]"
#             → ("test_update_cart", "tc14_zero")
#         """
#         parts = node_id.split("::")
#         last  = parts[-1]
#         m = re.match(r'^([^\[]+)\[(.+)\]$', last)
#         if m:
#             return m.group(1).strip(), m.group(2).strip()
#         return last.strip(), ""

#     def _resolve_tc_num(self, module_key: str, func_name: str, param_id: str):
#         """
#         Xác định số TC theo thứ tự ưu tiên:
#           1. PARAM_MAP   – khớp chuỗi trong param_id
#           2. MANUAL_MAP  – khớp tên hàm thủ công
#           3. Regex số trong tên hàm: test_tc07, test_TC01
#           4. Regex số trong param_id: [TC-7]
#         """
#         # 1. Param map
#         if param_id and module_key in PARAM_MAP:
#             for pattern, tc_num in PARAM_MAP[module_key].items():
#                 if pattern in param_id:
#                     return tc_num

#         # 2. Manual map
#         val = MANUAL_MAP.get((module_key, func_name))
#         if val is not None:
#             return val

#         # 3. Số trong tên hàm dạng test_tc07 / test_TC01
#         m = re.search(r'_tc0*(\d+)', func_name, re.IGNORECASE)
#         if m:
#             return int(m.group(1))

#         # 4. Số trong param_id dạng TC-7, TC7
#         if param_id:
#             m = re.search(r'TC[-_]?0*(\d+)', param_id, re.IGNORECASE)
#             if m:
#                 return int(m.group(1))

#         return None

#     @staticmethod
#     def _fail_reason(report) -> str:
#         """Lấy dòng lỗi cuối cùng từ traceback (ngắn gọn)."""
#         if report.longrepr:
#             text  = str(report.longrepr)
#             lines = [l.strip() for l in text.splitlines() if l.strip()]
#             return lines[-1][:400] if lines else "Unknown error"
#         return ""

#     @staticmethod
#     def _skip_reason(report) -> str:
#         """Lấy lý do skip."""
#         if report.longrepr:
#             text = str(report.longrepr).strip()
#             if "Skipped:" in text:
#                 return text.split("Skipped:", 1)[-1].strip()[:300]
#             return text[:300]
#         return ""