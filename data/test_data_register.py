
import random
import string


def random_suffix(length=6):
    """Sinh chuỗi ngẫu nhiên gồm chữ thường + số để tạo dữ liệu unique."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


# ---------------------------------------------------------------------------
# DỮ LIỆU DÙNG CHUNG (valid baseline) – dùng làm nền cho các test validation
# ---------------------------------------------------------------------------
VALID_HO_TEN    = "Vũ Thị Hồng"
VALID_SDT       = "0123456789"
VALID_DIA_CHI   = "Bắc Ninh"
VALID_GIOI_TINH = "nu"          # "nam" | "nu" – khớp với value radio button
VALID_NGAY_SINH = "2003-01-02"  
VALID_MAT_KHAU  = "123456"


def make_valid_email():
    """Tạo email unique mỗi lần gọi."""
    return f"test_{random_suffix()}@gmail.com"


def make_valid_username():
    """Tạo tài khoản unique mỗi lần gọi."""
    return f"user_{random_suffix()}"


# NHÓM 2 – VALIDATION: HỌ TÊN  (test case 7-15)
# ===========================================================================
# Mỗi tuple: (test_id, ho_ten, expected_result, error_type, description)
HO_TEN_CASES = [
    ("TC-7", "", "Vui lòng nhập thông tin vào đây", "html5", "Bỏ trống họ tên → HTML5 yêu cầu nhập"),
    ("TC-8", "hồng", "success_or_none", "none", "Họ tên chữ thường → hệ thống cho phép"),
    ("TC-9", "HỒNG", "success_or_none", "none", "Họ tên chữ in hoa → hệ thống cho phép"),
    ("TC-10", "hỒNg", "success_or_none", "none", "Họ tên hỗn hợp hoa/thường → hệ thống cho phép"),
    ("TC-11", "123", "Đăng ký không thành công. Thử lại sau !", "span", "Họ tên là số → không hợp lệ"),
    ("TC-12", "!@#", "Đăng ký không thành công. Thử lại sau !", "span", "Họ tên là ký tự đặc biệt → không hợp lệ"),
    ("TC-13", "hồng12", "success_or_none", "none", "Họ tên chữ thường + số → hệ thống cho phép"),
    ("TC-14", "hồng@#", "Đăng ký không thành công. Thử lại sau !", "span", "Họ tên chữ + ký tự đặc biệt → không hợp lệ"),
    ("TC-15", " hồng", "success_or_none", "none", "Họ tên chứa khoảng trắng đầu → hệ thống cho phép"),
]

# ===========================================================================
# NHÓM 3 – VALIDATION: SỐ ĐIỆN THOẠI  (test case 20–26)
# ===========================================================================
SDT_CASES = [
    (
        "TC-16",
        "",
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống SĐT → HTML5 báo lỗi"
    ),
    (
        "TC-17",
        "điện!@",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "SĐT là chữ/kí tự đặc biệt → không hợp lệ"
    ),
    (
        "TC-18",
        "0123 456 789",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "SĐT chứa khoảng trắng → không hợp lệ"
    ),
    (
        "TC-19",
        "1234567899",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "SĐT không bắt đầu bằng 0 → không hợp lệ"
    ),
    (
        "TC-20",
        "012345678",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "SĐT 9 ký tự (< 10) → không hợp lệ"
    ),
    (
        "TC-21",
        "0123456789",
        "success_or_none",
        "none",
        "SĐT hợp lệ 10 ký tự bắt đầu 0 → cho phép"
    ),
    (
        "TC-22",
        "01234567899",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "SĐT 11 ký tự (> 10) → không hợp lệ"
    ),
]

# ===========================================================================
# NHÓM 4 – VALIDATION: EMAIL 
# ===========================================================================
EMAIL_CASES = [
    (
        "TC-23",
        "",
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống Email"
    ),
    (
        "TC-24",
        "honggmail.com",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Email thiếu @ → không hợp lệ"
    ),
    (
        "TC-25",
        "hong@gmailcom",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Email thiếu dấu chấm → không hợp lệ"
    ),
    (
        "TC-26",
        "@gmail.com",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Email không có local part"
    ),
    (
        "TC-27",
        "hong@gmail",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Email không có TLD"
    ),
    # TC-28: email hợp lệ → dùng random để tránh trùng lặp
    # Được xử lý riêng trong test function (gọi make_valid_email())
]

# ===========================================================================
# NHÓM 5 – VALIDATION: MẬT KHẨU   
# ===========================================================================
MAT_KHAU_CASES = [
    (
        "TC-29",
        "",
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống mật khẩu"
    ),
    (
        "TC-30",
        "123456",
        "success_or_none",
        "none",
        "Mật khẩu hợp lệ ≥ 6 ký tự"
    ),
]

# ===========================================================================
# NHÓM 6 – VALIDATION: XÁC NHẬN MẬT KHẨU   
# ===========================================================================
XAC_NHAN_MK_CASES = [
    (
        "TC-31",
        "123456",
        "",           # xác nhận MK bỏ trống
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống xác nhận mật khẩu"
    ),
    (
        "TC-32",
        "123456",
        "1234567",    # xác nhận MK khác MK
        "Mật khẩu không khớp",
        "span",
        "Mật khẩu không khớp xác nhận"
    ),
    (
        "TC-33",
        "1234567",
        "1234567",    # xác nhận MK trùng MK
        "none",
        "none",
        "none"
    ),
]

# ===========================================================================
# NHÓM 7 – VALIDATION: TÀI KHOẢN   
# ===========================================================================
TAI_KHOAN_CASES = [
    (
        "TC-34",
        "",
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống tài khoản"
    ),
    (
        "TC-35",
        "vũ hồng",
        "success_or_none",
        "none",
        "Tài khoản chữ thường → cho phép"
    ),
    (
        "TC-36",
        "VŨ HỒNG",
        "success_or_none",
        "none",
        "Tài khoản chữ in hoa → cho phép"
    ),
    (
        "TC-37",
        "vŨ HồNg",
        "success_or_none",
        "none",
        "Tài khoản hoa + thường → cho phép"
    ),
    # (
    #     "TC-38",
    #     "123",
    #     "Đăng ký không thành công. Thử lại sau !",
    #     "span",
    #     "Tài khoản là số → không hợp lệ"
    # ),
    (
        "TC-38",
        "222",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Tài khoản là số → không hợp lệ"
    ),
    # (
    #     "TC-39",
    #     '!"£',
    #     "Đăng ký không thành công. Thử lại sau !",
    #     "span",
    #     "Tài khoản ký tự đặc biệt → không hợp lệ"
    # ),
    (
        "TC-39",
        '@@',
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Tài khoản ký tự đặc biệt → không hợp lệ"
    ),
    (
        "TC-40",
        "hồng25",
        "success_or_none",
        "none",
        "Tài khoản chữ + số → cho phép"
    ),
    # (
    #     "TC-41",
    #     "hồng@!",
    #     "Đăng ký không thành công. Thử lại sau !",
    #     "span",
    #     "Tài khoản chữ + ký tự đặc biệt → không hợp lệ"
    # ),
    (
        "TC-41",
        "hồng@@@",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Tài khoản chữ + ký tự đặc biệt → không hợp lệ"
    ),
    (
        "TC-42",
        " hồng",
        "success_or_none",
        "none",
        "Tài khoản chứa khoảng trắng đầu → cho phép"
    ),
]

# ===========================================================================
# NHÓM 8 – VALIDATION: ĐỊA CHỈ  
# ===========================================================================
DIA_CHI_CASES = [
    (
        "TC-43",
        "",
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống địa chỉ"
    ),
    (
        "TC-44",
        "Mão Điền Bắc Ninh",
        "success_or_none",
        "none",
        "Địa chỉ chữ thường → cho phép"
    ),
    (
        "TC-45",
        "MÃO ĐIỀN BẮC NINH",
        "success_or_none",
        "none",
        "Địa chỉ chữ in hoa → cho phép"
    ),
    (
        "TC-46",
        "bẮc ninh",
        "success_or_none",
        "none",
        "Địa chỉ hoa + thường → cho phép"
    ),
    (
        "TC-47",
        "123",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Địa chỉ là số → không hợp lệ"
    ),
    (
        "TC-48",
        "@@#",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Địa chỉ ký tự đặc biệt → không hợp lệ"
    ),
    (
        "TC-49",
        "3 xóm 3 Mão Điền",
        "success_or_none",
        "none",
        "Địa chỉ chữ + số → cho phép"
    ),
    (
        "TC-50",
        "3 xóm 3 - Mão Điền - Bắc Ninh",
        "success_or_none",
        "none",
        "Địa chỉ chữ + dấu gạch ngang → cho phép"
    ),
]

# ===========================================================================
# NHÓM 9 – VALIDATION: NGÀY SINH   
# ===========================================================================
NGAY_SINH_CASES = [
    (
        "TC-51",
        "",
        "Vui lòng nhập thông tin vào đây",
        "html5",
        "Bỏ trống ngày sinh"
    ),
    (
        "TC-52",
        "2003-01-01",
        "success_or_none",
        "none",
        "Ngày sinh hợp lệ trong quá khứ"
    ),
    (
        "TC-53",
        "0003-01-01",
        "Đăng ký không thành công. Thử lại sau !",
        "span",
        "Ngày sinh không hợp lệ"
    ),
]

# ===========================================================================
# NHÓM 10 – BUSINESS LOGIC  (test case 59–62)
# ===========================================================================
# Các case này được xử lý riêng trong test function do cần random email/username

# Thông báo lỗi từ hệ thống (span) – dùng làm hằng số tham chiếu
MSG_DUPLICATE_USERNAME = "Tên đăng nhập đã tồn tại"
MSG_DUPLICATE_EMAIL    = "Email đã tồn tại"
MSG_SYSTEM_ERROR       = "Lỗi hệ thống"
MSG_REGISTER_FAIL      = "Đăng ký không thành công. Thử lại sau !"
