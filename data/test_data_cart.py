
# ==============================================================
# THÔNG TIN TÀI KHOẢN TEST
# ==============================================================
VALID_USER     = "test_1"
VALID_PASSWORD = "123456789"

# TC-9, TC-10: Nút tăng (+) / giảm (-)
# tuple: (tc_id, hanh_dong, sl_dat_truoc, delta_mong_doi, mo_ta)
QTY_BUTTON_DATA = [
    (
        "tc9_increase",
        "increase",
        1,    
        +1,
        "TC-9: sl=1 < tồn kho → click (+) → sl tăng thành 2"
    ),
    (
        "tc10_decrease",
        "decrease",
        2,   
        -1,
        "TC-10: sl=2 > 1 → click (-) → sl giảm thành 1"
    ),
]


# ==============================================================
# TC-11: Click (+) khi sl = tồn kho → popup 'không đủ hàng'
# ==============================================================
QTY_MAX_STOCK = {
    "so_lan_click_max": 20,
    "expected_text"   : "không đủ",
}


# ==============================================================
# TC-12: Click (-) khi sl = 1 → popup xác nhận xóa → Cancel → SP còn
# ==============================================================
QTY_AT_ONE = {
    "sl_dat_truoc"  : 1,
    "expected_popup": "Xóa sản phẩm này khỏi giỏ hàng",
}


# ==============================================================
# TC-13 đến TC-20: Cập nhật giỏ hàng
# tuple: (tc_id, gia_tri_nhap, kich_ban, mo_ta)
# ==============================================================
UPDATE_CART_DATA = [
    (
        "tc13_zero",
        "0",
        "popup_confirm",
        "TC-13: Nhập sl=0 → Cập nhật → popup xác nhận xóa"
    ),
    (
        "tc14_negative",
        "-1",
        "reject",
        "TC-14: Nhập sl âm (-1) → không lưu số âm"
    ),
    (
        "tc15_float",
        "1.5",
        "reject",
        "TC-15: Nhập sl thực (1.5) → tự chuyển về số nguyên"
    ),
    (
        "tc16_text",
        "a",
        "reject",
        "TC-16: Nhập chữ ('a') → ô không nhận, giữ giá trị cũ"
    ),
    (
        "tc17_special",
        "!",
        "reject",
        "TC-17: Nhập ký tự đặc biệt ('!') → ô không nhận"
    ),
    (
        "tc18_empty",
        "",
        "reject",
        "TC-18: Bỏ trống → ở lại trang giỏ, yêu cầu nhập lại"
    ),
    (
        "tc19_valid",
        "2",
        "accept",
        "TC-19: Nhập sl hợp lệ (2) → cập nhật thành công"
    ),
    (
        "tc20_exceed",
        "100",
        "out_of_stock",
        "TC-20: Nhập sl vượt tồn kho (100) → 'Số lượng hàng trong kho không đủ'"
    ),
]

# ==============================================================
# TC-21, TC-24: Xóa SP – parametrize theo hành động popup
# tuple: (tc_id, hanh_dong_popup, ket_qua_mong_doi, mo_ta)
# ==============================================================
REMOVE_PRODUCT_DATA = [
    (
        "tc21_ok",
        "ok",
        "removed",
        "TC-22: Click × → OK → SP bị xóa khỏi giỏ"
    ),
    (
        "tc24_cancel",
        "cancel",
        "kept",
        "TC-24: Click × → Cancel → SP vẫn còn trong giỏ"
    ),
]

# ==============================================================
# TC-22: Xóa nhiều SP lần lượt
# ==============================================================
REMOVE_MULTIPLE = {
    "so_sp_toi_thieu": 3,   # thêm 3 SP khác nhau vào giỏ trước khi test
    "so_lan_xoa"     : 2,   # xóa 2 SP lần lượt
}

# ==============================================================
# TC-23: Xóa tất cả SP → giỏ rỗng
# ==============================================================
REMOVE_ALL = {
    "so_sp_toi_thieu": 3,                                      # đặc tả yêu cầu 3 SP
    "expected_text"  : "Chưa có sản phẩm nào trong giỏ hàng",
}