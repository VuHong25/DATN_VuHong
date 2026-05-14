

# ==============================================================
# TÀI KHOẢN TEST
# ==============================================================
ADMIN_USER     = "admin"
ADMIN_PASSWORD = "admin"

CUSTOMER_USER     = "test_1"
CUSTOMER_PASSWORD = "123456789"

# --- Hóa đơn CHƯA bị hủy ---

INVOICE_ACTIVE = {
    "description" : "Hóa đơn chưa bị hủy",
    "owner"       : CUSTOMER_USER,
    #   row_index=1 
    #   row_index=10 
    #   row_index=12 
    "row_index"   : 29,   
}

INVOICE_CANCELLED = {
    "description"     : "Hóa đơn đã bị hủy",
    "expected_status" : "Đã bị hủy",
    #   row_index=1 
    #   row_index=12
    "row_index"       : 3,   
}


# ==============================================================
# TC-1 / TC-2 : Quyền truy cập
# ==============================================================
ACCESS_ADMIN = {
    "username": ADMIN_USER,
    "password": ADMIN_PASSWORD,
}

# TC-2: Tài khoản khách hàng KHÔNG được vào trang admin
# Expected: Bị redirect về trang login HOẶC hiển thị thông báo không có quyền
ACCESS_CUSTOMER_NO_ADMIN = {
    "username"       : CUSTOMER_USER,
    "password"       : CUSTOMER_PASSWORD,
    "admin_invoice_url": "Admin/Invoice",   # URL thử truy cập trái phép
}


# ==============================================================
# TC-7: Xem danh sách hóa đơn
# ==============================================================
VIEW_INVOICE_LIST = {
    "min_row_count"    : 16,
    "expected_columns" : [
        "Tên khách hàng",
        "Tên người nhận",
        "Ngày đặt",
        "Địa chỉ nhận",
        "Trạng thái",
    ],
}


# ==============================================================
# TC-10: Xem chi tiết hóa đơn
# ==============================================================
VIEW_INVOICE_DETAIL = {
    "row_index"      : INVOICE_ACTIVE["row_index"],
    "expected_fields": [
        "Tên người đặt",
        "Tên người nhận",
        "Ngày đặt",
        "Trạng thái",
        "Số điện thoại",
        "Địa chỉ nhận",
    ],
}


# ==============================================================
# TC-12: Cập nhật trạng thái
# ==============================================================
STATUS_OPTIONS = ["Đang giao", "Đang chuẩn bị", "Đã thanh toán"]

# Parametrize data: (tc_id, status_text, mo_ta)
# Mỗi phần tử = 1 lần chạy test với 1 trạng thái khác nhau
UPDATE_STATUS_DATA = [
    (
        "tc12_dang_giao",
        "Đang giao",
        "TC-12: Admin chọn 'Đang giao' → hệ thống cập nhật"
    ),
    # (
    #     "tc12_dang_chuan_bi",
    #     "Đang chuẩn bị",
    #     "TC-12: Admin chọn 'Đang chuẩn bị' → hệ thống cập nhật"
    # ),
    # (
    #     "tc12_da_thanh_toan",
    #     "Đã thanh toán",
    #     "TC-12: Admin chọn 'Đã thanh toán' → hệ thống cập nhật"
    # ),
]


# ==========================================================
# TC-13: Hủy → click OK  → trạng thái đổi "Đã bị hủy"
# TC-14: Hủy → click Cancel → đơn hàng giữ nguyên
# ==============================================================
CANCEL_ORDER = {
    # Dùng cùng row_index với INVOICE_ACTIVE
    "row_index"       : INVOICE_ACTIVE["row_index"],
    # Text xuất hiện trong SweetAlert title
    "confirm_text"    : "Bạn có chắc về việc hủy đơn hàng này!",
    # Trạng thái sau khi hủy thành công
    "expected_status" : "Đã bị hủy",
}


# ==============================================================
# THÔNG BÁO HỆ THỐNG
# ==============================================================
MESSAGES = {
    # TC-8: Thông báo khi không có hóa đơn
    "no_invoice"       : "Không có đơn hàng",
    # TC-13/14: Text trong SweetAlert khi hủy đơn
    "cancel_confirm"   : "Bạn có chắc về việc hủy đơn hàng này!",
    # Trạng thái đơn đã hủy (xuất hiện trong page_source sau khi hủy)
    "cancelled_status" : "Đã bị hủy",
    # TC-9: Lỗi DB (cần mock → skip)
    "system_error"     : "Lỗi hệ thống",
}
