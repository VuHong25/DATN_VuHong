

import pytest
from pages.search_page import SearchPage
from conftest import base_url
from data.test_data_search import (
    SEARCH_FOUND_DATA,
    SEARCH_NOT_FOUND_DATA,
    SEARCH_EMPTY_DATA,
    SEARCH_DUPLICATE_DATA,
)

# ============================================================
# NHÓM 1: QUYỀN TRUY CẬP (TC-1, 2)
# ============================================================

class TestSearchAccess:
  
    def test_search_without_login(self, driver):
      
        page = SearchPage(driver)
        page.open_home(base_url)
        page.search("Áo phông nam trơn")

        has_products = page.get_product_count() > 0
        has_not_found = page.is_not_found_visible()

        assert has_products or has_not_found, (
            "[TC-1] Hệ thống phải cho phép tìm kiếm khi chưa đăng nhập "
            "(phải hiển thị kết quả hoặc thông báo not-found, không redirect sang login)."
        )

    def test_search_with_login(self, logged_in_driver):
      
        page = SearchPage(logged_in_driver)
        page.open_home(base_url)
        page.search("Áo phông nam trơn")

        has_products = page.get_product_count() > 0
        has_not_found = page.is_not_found_visible()

        assert has_products or has_not_found, (
            "[TC-2] Hệ thống phải cho phép tìm kiếm khi đã đăng nhập."
        )


# ============================================================
# NHÓM 3: TÌM KIẾM THÀNH CÔNG 
# ============================================================

class TestSearchFound:
    @pytest.mark.parametrize(
        "keyword, submit_by, expected_fragment, test_id",
        SEARCH_FOUND_DATA,
        ids=[row[3] for row in SEARCH_FOUND_DATA],
    )
    def test_search_returns_products(self, logged_in_driver, keyword, submit_by, expected_fragment, test_id):

        page = SearchPage(logged_in_driver)
        page.open_home(base_url)

        if submit_by == "enter":
            page.search_by_enter(keyword)
        else:
            page.search(keyword)
        count = page.get_product_count()

        assert count > 0, (
            f"[{test_id}] Tìm kiếm '{keyword}' phải trả về ít nhất 1 sản phẩm, "
            f"nhưng không tìm thấy sản phẩm nào."
        )
        
        names = page.get_product_names()
        match = any(expected_fragment in name for name in names)
        assert match, (
            f"[{test_id}] Kết quả phải chứa sản phẩm liên quan đến '{expected_fragment}'. "
            f"Tên sản phẩm thực tế: {names}"
        )


# ============================================================
# NHÓM 4: TÌM KIẾM KHÔNG TÌM THẤY ====

class TestSearchNotFound:

    @pytest.mark.parametrize(
        "keyword, submit_by, expected_msg_fragment, test_id",
        SEARCH_NOT_FOUND_DATA,
        ids=[row[3] for row in SEARCH_NOT_FOUND_DATA],
    )
    def test_search_shows_not_found_message(
        self, logged_in_driver, keyword, submit_by, expected_msg_fragment, test_id
    ):
        """
        Luồng: mở trang → tìm kiếm → kiểm tra không có sản phẩm + thông báo đúng.
        """
        page = SearchPage(logged_in_driver)
        page.open_home(base_url)

        if submit_by == "enter":
            page.search_by_enter(keyword)
        else:
            page.search(keyword)

        # 1. Không được hiển thị sản phẩm nào
        count = page.get_product_count()
        assert count == 0, (
            f"[{test_id}] Từ khóa '{keyword}' không hợp lệ/không tồn tại, "
            f"nhưng hệ thống vẫn hiển thị {count} sản phẩm."
        )

        # 2. Thông báo not-found phải hiển thị
        assert page.is_not_found_visible(), (
            f"[{test_id}] Phải hiển thị thông báo 'Không tìm thấy sản phẩm nào' "
            f"khi tìm kiếm '{keyword}', nhưng thông báo không xuất hiện."
        )

        # 3. Nội dung thông báo phải chứa text kỳ vọng (không phân biệt hoa/thường)
        actual_msg = page.get_not_found_text()
        assert expected_msg_fragment.lower() in actual_msg.lower(), (
            f"[{test_id}] Thông báo không đúng nội dung.\n"
            f"  Kỳ vọng chứa : '{expected_msg_fragment}'\n"
            f"  Thực tế      : '{actual_msg}'"
        )


# ============================================================
# NHÓM 5: BỎ TRỐNG → HIỂN THỊ TẤT CẢ SẢN PHẨM (TC-7)
# ============================================================

class TestSearchEmpty:
 
    @pytest.mark.parametrize(
        "keyword, submit_by, test_id",
        SEARCH_EMPTY_DATA,
        ids=[row[2] for row in SEARCH_EMPTY_DATA],
    )
    def test_search_empty_shows_all_products(
        self, logged_in_driver, keyword, submit_by, test_id
    ):
        page = SearchPage(logged_in_driver)
        page.open_home(base_url)
        page.search(keyword)   # keyword = ""

        count = page.get_product_count()
        assert count >= 1, (
            f"[{test_id}] Bỏ trống tìm kiếm phải hiển thị tất cả sản phẩm "
            f"(ít nhất 1), nhưng chỉ thấy {count}."
        )

        assert not page.is_not_found_visible(), (
            f"[{test_id}] Khi bỏ trống, không được hiển thị thông báo 'Không tìm thấy'."
        )


# ============================================================
# NHÓM 6: SẢN PHẨM TRÙNG TÊN (TC-15)
# ============================================================

class TestSearchDuplicate:
    """
    Kiểm tra: từ khóa trùng với nhiều sản phẩm → hiển thị tất cả sản phẩm đó.
    """

    @pytest.mark.parametrize(
        "keyword, min_count, test_id",
        SEARCH_DUPLICATE_DATA,
        ids=[row[2] for row in SEARCH_DUPLICATE_DATA],
    )
    def test_search_duplicate_returns_all(
        self, logged_in_driver, keyword, min_count, test_id
    ):
        
        page = SearchPage(logged_in_driver)
        page.open_home(base_url)
        page.search(keyword)

        count = page.get_product_count()
        assert count >= min_count, (
            f"[{test_id}] Từ khóa '{keyword}' có {min_count} sản phẩm trùng tên, "
            f"nhưng kết quả chỉ hiển thị {count}."
        )


