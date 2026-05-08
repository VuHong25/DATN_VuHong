
#7
PRODUCT_ADD_TO_CART_SUCCESS = {
    "keyword": "Áo ba lỗ",
    "size_to_select": None, 
    "expected_swal_auto_disappear": True,
    "expected_swal_title_keywords": ["thành công"],
    "expected_swal_text_keywords" : ["giỏ hàng"],
    "expected_swal_title_variants": [
        "Thành công!",
        "Thành Công!",
        "thành công",
    ],
    "expected_swal_text_variants": [
        "xem chi tiết tại giỏ hàng nhé <3",
        "xem chi tiết tại giỏ hàng",
        "giỏ hàng",
    ],
}

# TC-8 dùng lại data TC-7 (thêm precondition đã đăng nhập)
PRODUCT_ADD_TO_CART_OUT_OF_STOCK = {
    "keyword"            : "Quần jean nữ ôm body",
    "expected_has_name"  : True,
    "expected_has_price" : True,
    "expected_has_image" : True,
    "expected_btn_disabled": True,
    "expected_swal_title_keywords": ["hết hàng"],
    "expected_swal_title_variants": [
        "Hết hàng!",
        "Hết hàng",
        "HẾT HÀNG",
        "Thông báo",
    ],
}


# TC-9 dùng lại data TC-8 (thêm precondition đã đăng nhập)
PRODUCT_ADD_TO_CART_OUT_OF_SIZE = {
    "keyword"               : "Áo phông nam trơn",
    "out_of_size"           : "Size XXXL",  # text option trong dropdown
    "out_of_size_contains"  : "XXXL",       # dùng contains để linh hoạt hơn
    "available_size"        : "Size M",     # size còn hàng để test ngược lại
    "expected_has_name"     : True,
    "expected_has_price"    : True,
    "expected_has_image"    : True,
    "expected_has_size_dropdown": True,
    "expected_btn_disabled_for_out_size": True,
    # SweetAlert xuất hiện sau khi chọn size hết
    "expected_swal_text_keywords": ["số lượng", "kho không đủ", "không đủ"],
    "expected_swal_title_keywords": ["thông báo", "cảnh báo"],
}


# ----------------------------------------------------------
# TC-10: Nhập SL > tồn kho
# Precondition: Đã đăng nhập, "Áo ba lỗ" còn hàng
# Expected: SweetAlert "Số lượng hàng trong kho không đủ"
# ----------------------------------------------------------
PRODUCT_EXCEED_QUANTITY = {
    "keyword"      : "Áo ba lỗ",
    "exceed_qty"   : 1000,  # Chắc chắn > tồn kho thực tế
    "expected_swal_text_keywords": ["số lượng", "kho không đủ", "không đủ"],
}

# TIMEOUT SETTINGS
# ----------------------------------------------------------
DEFAULT_TIMEOUT        = 7   # giây – chờ element xuất hiện
SWAL_APPEAR_TIMEOUT    = 3    # giây – chờ SweetAlert xuất hiện
SWAL_DISAPPEAR_TIMEOUT = 3   # giây – chờ SweetAlert tự tắt (TC-12)
















