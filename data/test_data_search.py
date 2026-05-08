# ============================================================
# FILE: data/search_data.py
# ------------------------------------------------------------------
# NHÓM 1: Tìm kiếm THÀNH CÔNG – trả về sản phẩm
# Test case: Tìm kiếm-22, 13, 14, 16, 17, 23
# Cấu trúc mỗi tuple: (keyword, submit_by, expected_name_fragment, test_id)
SEARCH_FOUND_DATA = [
   
    ("Áo sơ mi nam trơn", "button", "áo sơ mi nam trơn", "TK-21"),

    ("áO", "button", "áo", "TK-13"),

    ("ÁO", "button", "áo", "TK-14"),

    ("a", "button", "a", "TK-16"),

    ("Áo sơ mi", "enter",  "áo sơ mi", "TK-17"),

    ("Quần jean nữ ôm body", "button", "quần jean nữ ôm body", "TK-22"),
]


# ------------------------------------------------------------------
# NHÓM 2: Tìm kiếm KHÔNG TÌM THẤY – hiển thị thông báo
# Cấu trúc mỗi tuple: (keyword, submit_by, expected_msg_fragment, test_id)
#   expected_msg_fragment: chuỗi con kỳ vọng xuất hiện trong thông báo

# ------------------------------------------------------------------
SEARCH_NOT_FOUND_DATA = [
    # TC-8: Từ khóa là ký tự đặc biệt
    ("@@@",         "button", "Không tìm thấy sản phẩm nào cho từ khóa: @@@",    "TK-8"),

    # TC-9: Từ khóa là số
    ("123",         "button", "Không tìm thấy sản phẩm nào cho từ khóa: 123",    "TK-9"),

    # TC-10: Chữ + số
    ("Áo12",        "button", "Không tìm thấy sản phẩm nào cho từ khóa: Áo12",   "TK-10"),

    # TC-11: Chữ + ký tự đặc biệt
    ("Áo@@@",       "button", "Không tìm thấy sản phẩm nào cho từ khóa: Áo@@@",  "TK-11"),

    # TC-12: Số + ký tự đặc biệt
    ("12@",         "button", "Không tìm thấy sản phẩm nào cho từ khóa: 12@",    "TK-12"),

    # TC-18: Từ khóa tiếng Việt không dấu
    ("Ao ba lo",    "button", "Không tìm thấy sản phẩm nào cho từ khóa: Ao ba lo", "TK-18"),

    # TC-19: Từ khóa sai chính tả
    ("Áo thun lam", "button", "Không tìm thấy sản phẩm nào cho từ khóa: Áo thun lam", "TK-19"),

    # TC-20: Từ khóa có khoảng trắng ở đầu/cuối
    (" Áo sơ mi ",  "button", "Không tìm thấy sản phẩm nào",                      "TK-20"),

    # TC-23: Từ khóa không tồn tại trong DB
    ("Áo dài",      "button", "Không tìm thấy sản phẩm nào",                      "TK-23"),
]

# ------------------------------------------------------------------
# NHÓM 3: BỎ TRỐNG ô tìm kiếm → hiển thị TẤT CẢ sản phẩm
# Test case: Tìm kiếm-7
# Cấu trúc: (keyword, submit_by, test_id)
# ------------------------------------------------------------------
SEARCH_EMPTY_DATA = [
    ("", "button", "TK-7"),
]


# ------------------------------------------------------------------
# NHÓM 4: TÌM KIẾM SẢN PHẨM TRÙNG TÊN
# Test case: Tìm kiếm-15
# Cấu trúc: (keyword, min_count, test_id)
#   min_count: số sản phẩm tối thiểu kỳ vọng trong kết quả
# ------------------------------------------------------------------
SEARCH_DUPLICATE_DATA = [
    ("Quần khaki nam slimfit", 2, "TK-15"),
]


















