
# ----------------------------------------------------------
# TC-7: SP còn hàng
# Precondition: "Áo phông nữ in họa tiết" có số lượng > 0
# Expected: Hiển thị đầy đủ tên, giá, ảnh, size dropdown, nút enabled
# ----------------------------------------------------------
PRODUCT_IN_STOCK = {
    "keyword": "Áo phông nữ in họa tiết",
    "expected_has_name"           : True,
    "expected_has_price"          : True,
    "expected_has_image"          : True,
    "expected_has_size_dropdown"  : True,
    "expected_add_btn_enabled"    : True,
}

PRODUCT_OUT_OF_STOCK = {
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


PRODUCT_OUT_OF_SIZE = {
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
# TC-10: SP có đánh giá
# Precondition: "Áo sơ mi nam trơn" đã có khách đánh giá trong DB
# Expected: Section đánh giá hiển thị thông tin reviewer, bình luận, ngày
# ----------------------------------------------------------
PRODUCT_WITH_REVIEW = {
    "keyword": "Áo sơ mi nam trơn",
    "expected_has_review_section": True,
}

# ----------------------------------------------------------
# TC-11: SP CHƯA có đánh giá
# Precondition: "Áo phông nữ in họa tiết" chưa có ai đánh giá
# Expected: Text TĨNH "Chưa có đánh giá nào" trong section đánh giá
# KHÔNG phải popup SweetAlert
# ----------------------------------------------------------
PRODUCT_NO_REVIEW = {
    "keyword": "Áo phông nữ in họa tiết",
    "expected_no_review_text": "Chưa có đánh giá nào",
}

# ----------------------------------------------------------
# TIMEOUT SETTINGS
# ----------------------------------------------------------
DEFAULT_TIMEOUT        = 10   # giây
SWAL_APPEAR_TIMEOUT    = 5    # chờ popup SweetAlert xuất hiện
SWAL_DISAPPEAR_TIMEOUT = 8    # chờ popup SweetAlert tự tắt

# ----------------------------------------------------------
# PARAMETRIZE: ACCESS RIGHT (TC-1, TC-2)
# Format: (tc_id, mo_ta, need_login)
# ----------------------------------------------------------
ACCESS_RIGHT_PARAMS = [
    ("TC-1", "Chưa đăng nhập vẫn xem được chi tiết SP", False),
    ("TC-2", "Đã đăng nhập vẫn xem được chi tiết SP",   True),
]




