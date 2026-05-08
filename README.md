# TrueMart – Selenium WebDriver Testing Project

> **Đề tài:** Nghiên cứu và ứng dụng Selenium WebDriver trong kiểm thử website bán quần áo TrueMart

## Giới thiệu dự án
Đồ án về Kiểm thử phần mềm, ứng dụng python + selenium webdriver cho website thương mại điện tử bán quần áo TrueMart

### Mục tiêu
- Nghiên cứu lý thuyết về kiểm thử phần mềm: test case design, Selenium WebDriver, Page Object Model.
- Thiết kế bộ test case đầy đủ cho 8 chức năng cốt lõi của TrueMart.
- Viết automation test script sử dụng Selenium WebDriver + pytest
- Phân tích kết quả, tổng hợp báo cáo kiểm thử.

### Phạm vi kiểm thử
Kiểm thử tự động: Function testing 
Kiểm thử thủ công: UI testing

---

## Công nghệ sử dụng
            Công nghệ                   | Phiên bản
1           Python                          3.12.2
2           Selenium Webdriver              4.43.0
3           pytest                          9.0.3
4           pytest-html                     4.2.0 
5           webdriver-manager               4.0.2

## Cấu trúc thư mục

DO_AN/
├── conftest.py                        
├── data/
|   ├── test_data_cart.py                  
│   ├── test_data_add_to_cart.py                  
│   ├── test_data_invoice.py              
│   └── test_data_login.py                
|   ├── test_data_order.py                
│   ├── test_data_product.py                 
│   ├── test_data_register.py              
│   └── test_data_search.py  
├── pages/
│   ├── base_page.py                   ← Lớp cơ sở (hành động dùng chung)
│   ├── cart_page.py                  
│   ├── add_to_cart_page.py            
│   └── invoice_page.py            
│   ├── login_page.py                
│   ├── order_page.py                 
│   ├── register_page.py             
│   └── search_page.py  
├── tests/                         
├── ├── test_cart.py                 
│   ├── test_add_to_cart.py                 
│   ├── test_invoice.py            
│   └── test_login.py                
│   ├── test_order.py                  
│   ├── test_product.py                 
│   ├── test_register.py          
│   └── test_search.py
├── documents/
│   └── Template_Test_Case.xlsx 
|   └── US.docx                  
├── reports/                       
│   └── test-report.html            # Báo cáo kết quả kiểm thử
├── screenshots/                  # Ảnh chụp màn hình khi fail
└── README.md


## Cài đặt và chạy

### Bước 1: Cài python packages

pip install selenium pytest

### Bước 2: Cài ChromeDriver
pip install webdriver-manager

### Bước 3: Cài môi trường ảo
- Tạo thư mục project: python -m venv .venv
- Kích hoạt môi trường ảo: .venv\Scripts\activate
- Chọn interpreter trong VS Code
    Nhấn Ctrl + Shift + P
    Gõ: Python: Select Interpreter
    Chọn: .venv\Scripts\python.exe

### Bước 4: Chạy một chức năng cụ thể

# Chạy tất cả
# Công thức chung: pytest file::class::testcase -v
cd tests
pytest -v

# Chỉ chạy 1 module
pytest test_login.py -v

# Chạy 1 test case cụ thể
pytest test_login.py::TestLogin::test_login_success -v

# Chạy và xuất báo cáo HTML
pytest -v --html=reports.html

# Chạy test + xuất report cho 1 chức năng 
# Công thức chung: pytest file::class::testcase -v --html=reports/test_report.html --self-contained-html
pytest test_cart.py -v --html=reports/test_report.html --self-contained-html

# Chạy test + xuất report cho 1 case
pytest tests/test_cart.py::TestCartAccessRight::test_view_cart_not_logged_in
-v --html=reports/test_report.html --self-contained-html

## Các chức năng được kiểm thử

### 1. Đăng nhập 

### 2. Tìm kiếm sản phẩm 

### 3. Xem danh mục sản phẩm

### 4. Xem chi tiết sản phẩm  

### 5. Đăng ký tài khoản

### 6. Đặt hàng 

### 7. Quản lý giỏ hàng 

### 8. Quản lý hóa đơn 

## Tài liệu liên quan

Đặc tả Use Case                    
Template Test Case         
Báo cáo đồ án              
Slide thuyết trình         

## Ghi chú

- Website TrueMart được triển khai trên môi trường localhost. Để chạy test, cần khởi động server trước.
- ChromeDriver phải tương thích với phiên bản Chrome đang cài đặt.
- Một số test case yêu cầu dữ liệu seed trước trong database (ví dụ: có ít nhất 1 sản phẩm, 1 hóa đơn).
- phải đổi invoice_active ở file data để tc14 pass 