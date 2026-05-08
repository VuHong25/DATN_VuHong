
# ==============================================================
# THÔNG TIN TÀI KHOẢN TEST
# ==============================================================
VALID_USER     = "test_1"
VALID_PASSWORD = "123456789"

# ==============================================================
# THÔNG TIN NHẬN HÀNG MẶC ĐỊNH
# Khớp với dữ liệu tài khoản test_1 trong DB.
# TC-7: Giữ nguyên thông tin → hệ thống lấy mặc định
# ==============================================================
DEFAULT_RECEIVER = {
    "ho_ten"  : "Thử",
    "sdt"     : "0123654789",
    "dia_chi" : "Mão Điền",
    "ghi_chu" : "Che tên sản phẩm",
}

# ==============================================================
# TC-8: Thay đổi thông tin nhận hàng trước khi đặt
# ==============================================================
CHANGED_RECEIVER = {
    "ho_ten"  : "Hồng",
    "sdt"     : "0123654789",
    "dia_chi" : "Mão Điền",
    "ghi_chu" : "Che tên sản phẩm",
}

# ==============================================================
# TC-9: Bỏ trống từng field → HTML5 required validation

# tuple: (tc_id, ho_ten, sdt, dia_chi, ghi_chu, field_to_check, mo_ta)

EMPTY_FIELD_DATA = [
    (
        "tc9_empty_ho_ten",
        "",    # ho_ten bỏ trống
        None,  # sdt giữ nguyên
        None,  # dia_chi giữ nguyên
        None,  # ghi_chu giữ nguyên
        "ho_ten",
        "TC-9a: Bỏ trống Họ tên → HTML5 báo lỗi required"
    ),
    # (
    #     "tc9_empty_sdt",
    #     None,
    #     "",    # sdt bỏ trống
    #     None,
    #     None,
    #     "sdt",
    #     "TC-9b: Bỏ trống Số điện thoại → HTML5 báo lỗi required"
    # ),
    # (
    #     "tc9_empty_dia_chi",
    #     None,
    #     None,
    #     "",    # dia_chi bỏ trống
    #     None,
    #     "dia_chi",
    #     "TC-9c: Bỏ trống Địa chỉ → HTML5 báo lỗi required"
    # ),
]

# ==============================================================
# TC-10: Đặt hàng thành công (Biz – happy path)
# tuple: (tc_id, mo_ta)
ORDER_SUCCESS_DATA = [
    (
        "tc10_success_default_info",
        "TC-10: Đặt hàng thành công, giữ nguyên thông tin mặc định"
    ),
]

ORDER_EMPTY_CART = {
    "tc_id" : "tc11_order_empty_cart",
    "mo_ta" : "TC-11: Giỏ rỗng → nút Đặt hàng không hoạt động / bị ẩn"
}
