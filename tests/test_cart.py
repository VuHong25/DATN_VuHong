
import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.cart_page import CartPage
from conftest import base_url, LOGIN_PASSWORD, LOGIN_USERNAME
from data.test_data_cart import (
    # UI_BUTTON_DATA,
    # UI_BUTTON_ENABLE_DATA,
    QTY_BUTTON_DATA,
    QTY_MAX_STOCK,
    QTY_AT_ONE,
    UPDATE_CART_DATA,
    REMOVE_PRODUCT_DATA,
    REMOVE_MULTIPLE,
    REMOVE_ALL,
)


# ==============================================================
# HELPER DÙNG CHUNG
# ==============================================================

def ensure_cart_has_product(page: CartPage, base_url: str):
    """
    Đảm bảo giỏ hàng có ít nhất 1 SP.
    Nếu chưa có → thêm theo đúng luồng thực tế.
    Nếu vẫn không thêm được → skip.
    """
    if page.get_cart_item_count() == 0:
        page.add_product_to_cart(base_url)
    if page.get_cart_item_count() == 0:
        pytest.skip(
            "Không thể thêm SP tự động – "
            "kiểm tra locator FIRST_PRODUCT_LINK và BTN_ADD_TO_CART"
        )


# ==============================================================
# NHÓM 1: ACCESS RIGHT  –  TC-1, TC-2
# ==============================================================
class TestCartAccessRight:

    def test_view_cart_not_logged_in(self, driver):
        """TC-1: Chưa đăng nhập → click giỏ hàng → không redirect login."""
        page = CartPage(driver)
        page.open_cart(base_url)
        assert "login" not in driver.current_url.lower(), \
            "TC-1: Khách chưa đăng nhập phải được phép xem giỏ hàng"

    def test_view_cart_logged_in(self, logged_in_driver):
        """TC-2: Đã đăng nhập → hiện SP hoặc thông báo giỏ rỗng."""
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        has_items = page.get_cart_item_count() > 0
        has_empty = page.is_empty_cart_visible()
        assert has_items or has_empty, \
            "TC-2: Giỏ hàng phải hiện SP hoặc thông báo rỗng"



# ==============================================================
# NHÓM 3: BIZ – Xem giỏ hàng  –  TC-7, TC-8
# ==============================================================
class TestCartView:

    def test_view_cart_with_items(self, logged_in_driver):
        """TC-7: Giỏ có SP → hiển thị đầy đủ thông tin."""
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        ensure_cart_has_product(page, base_url)
        assert page.get_cart_item_count() > 0, \
            "TC-7: Phải hiện ít nhất 1 SP trong giỏ"

    def test_view_empty_cart(self, logged_in_driver):
        """
        TC-8: Giỏ rỗng → hiện 'Chưa có sản phẩm nào trong giỏ hàng'.
        """
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        if page.get_cart_item_count() > 0:
            pytest.skip("TC-8: Giỏ đang có hàng – cần xóa hết trước")
        assert page.is_empty_cart_visible(), \
            "TC-8: Phải hiện 'Chưa có sản phẩm nào trong giỏ hàng'"


# ==============================================================
# NHÓM 4: BIZ – Nút (+) và (-)  –  TC-14, TC-15, TC-16, TC-17
# ==============================================================
class TestCartQuantityButtons:
    @pytest.mark.parametrize(
        "tc_id, hanh_dong, sl_dat_truoc, delta, mo_ta",
        QTY_BUTTON_DATA,
        ids=[d[0] for d in QTY_BUTTON_DATA],
    )
    def test_qty_button(self, logged_in_driver, tc_id, hanh_dong, sl_dat_truoc, delta, mo_ta):
        """TC-9: click (+) → tăng 1.  TC-10: click (-) → giảm 1."""
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        ensure_cart_has_product(page, base_url)
        page.set_quantity_of(index=0, value=str(sl_dat_truoc))
        page.click_update_cart()
        WebDriverWait(logged_in_driver, 5).until(
            lambda d: page.get_quantity_of(index=0) == sl_dat_truoc
        )
        qty_before = page.get_quantity_of(index=0)
        if hanh_dong == "increase":
            page.click_increase(index=0)
        else:
            page.click_decrease(index=0)
        WebDriverWait(logged_in_driver, 5).until(
            lambda d: page.get_quantity_of(index=0) != qty_before
        )
        qty_after = page.get_quantity_of(index=0)
        assert qty_after == qty_before + delta, \
            f"[{tc_id}] {mo_ta} | Trước: {qty_before}, Sau: {qty_after}, Delta: {delta}"

    def test_increase_exceeds_stock(self, logged_in_driver):
        """TC-11: Click (+) đến max stock → popup 'không đủ hàng'."""
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        ensure_cart_has_product(page, base_url)

        max_clicks  = QTY_MAX_STOCK["so_lan_click_max"]
        expect_text = QTY_MAX_STOCK["expected_text"]

        found = False
        for _ in range(max_clicks):
            page.click_increase(index=0)
            if page.wait_for_swal_appear(timeout=2):
                found = True
                break

        if not found:
            pytest.skip(f"TC-11: Chưa đạt max stock sau {max_clicks} lần click")

        swal_text = page.get_swal_text()
        assert expect_text in swal_text.lower(), \
            f"TC-11: Phải có '{expect_text}' trong popup. Thực tế: {swal_text}"
        page.close_swal()

    def test_decrease_at_qty_one_shows_popup(self, logged_in_driver):
        """TC-12: sl=1, click (-) → popup xác nhận → Cancel → SP còn."""
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        ensure_cart_has_product(page, base_url)

        sl = QTY_AT_ONE["sl_dat_truoc"]
        page.set_quantity_of(index=0, value=str(sl))
        page.click_update_cart()
        WebDriverWait(logged_in_driver, 5).until(
            lambda d: page.get_quantity_of(index=0) == sl
        )

        count_before = page.get_cart_item_count()
        page.click_decrease(index=0)
        WebDriverWait(logged_in_driver, 5).until(
            lambda d: page.is_confirm_popup_visible()
        )
        assert page.is_confirm_popup_visible(), \
            "TC-12: Phải hiện popup xác nhận xóa khi sl = 1"

        page.cancel_delete()
        assert page.get_cart_item_count() == count_before, \
            f"TC-12: Click Cancel → SP phải vẫn còn. Trước: {count_before}"


# ==============================================================
# NHÓM 5: BIZ – Cập nhật giỏ hàng  –  TC-13 đến TC-20
# ==============================================================
class TestCartUpdate:

    def _prepare(self, page: CartPage):
        page.open_cart(base_url)
        ensure_cart_has_product(page, base_url)

    @pytest.mark.parametrize(
        "tc_id, gia_tri_nhap, kich_ban, mo_ta",
        UPDATE_CART_DATA,
        ids=[d[0] for d in UPDATE_CART_DATA],
    )
    def test_update_cart(self, logged_in_driver, tc_id, gia_tri_nhap, kich_ban, mo_ta):
        """TC-13 đến TC-20: Cập nhật giỏ với nhiều loại input."""
        page = CartPage(logged_in_driver)
        self._prepare(page)

        page.set_quantity_of(index=0, value=gia_tri_nhap)
        page.click_update_cart()

        if kich_ban == "popup_confirm":
            WebDriverWait(logged_in_driver, 5).until(
                lambda d: page.is_confirm_popup_visible() or page.is_swal_visible()
            )
            assert page.is_confirm_popup_visible() or page.is_swal_visible(), \
                f"[{tc_id}] {mo_ta} | Phải hiện popup xác nhận xóa"
            page.confirm_delete()

        elif kich_ban == "reject":
            page.wait_for_cart_update()
            still_on_cart = (
                "cart"  in logged_in_driver.current_url.lower()
                or "order" in logged_in_driver.current_url.lower()
            )
            assert still_on_cart, f"[{tc_id}] {mo_ta} | Phải ở lại trang giỏ hàng"

            if gia_tri_nhap == "":
                is_err_visible = page.is_error_message_displayed()
                assert is_err_visible, \
                    f"[{tc_id}] BUG: Không hiện thông báo 'Vui lòng nhập số lượng'!"
                actual_total = page.get_total_price_text(index=0)
                assert "NaN" not in actual_total, \
                    f"[{tc_id}] BUG: Cột thành tiền hiện '{actual_total}'"

            if gia_tri_nhap.lstrip("-").replace(".", "").isdigit():
                qty = page.get_quantity_of(index=0)
                assert qty >= 0, f"[{tc_id}] LỖI: Hệ thống lưu số âm!"
                if "." in str(gia_tri_nhap):
                    assert float(qty).is_integer(), \
                        f"[{tc_id}] BUG: Nhập {gia_tri_nhap} nhưng không làm tròn: {qty}"

        elif kich_ban == "accept":
            expected_qty = int(float(gia_tri_nhap))
            WebDriverWait(logged_in_driver, 5).until(
                lambda d: page.get_quantity_of(index=0) == expected_qty
            )
            assert page.get_quantity_of(index=0) == expected_qty, \
                f"[{tc_id}] {mo_ta} | Sl phải = {expected_qty}"

        elif kich_ban == "out_of_stock":
            appeared = page.wait_for_swal_appear(timeout=5)
            assert appeared, f"[{tc_id}] {mo_ta} | Phải hiện SweetAlert không đủ hàng"
            swal_text = page.get_swal_text()
            assert "không đủ" in swal_text.lower(), \
                f"[{tc_id}] {mo_ta} | Phải có 'không đủ'. Thực tế: {swal_text}"
            page.close_swal()


# ==============================================================
# NHÓM 6: BIZ – Xóa sản phẩm  –  21-24
# ==============================================================
class TestCartRemove:

    def _prepare(self, page: CartPage):
        page.open_cart(base_url)
        ensure_cart_has_product(page, base_url)

    @pytest.mark.parametrize(
        "tc_id, hanh_dong_popup, ket_qua, mo_ta",
        REMOVE_PRODUCT_DATA,
        ids=[d[0] for d in REMOVE_PRODUCT_DATA],
    )
    def test_remove_product(self, logged_in_driver, tc_id, hanh_dong_popup, ket_qua, mo_ta):
        page = CartPage(logged_in_driver)
        self._prepare(page)

        count_before = page.get_cart_item_count()
        page.click_remove(index=0)

        WebDriverWait(logged_in_driver, 5).until(
            lambda d: page.is_confirm_popup_visible()
        )
        assert page.is_confirm_popup_visible(), \
            f"[{tc_id}] Phải hiện popup xác nhận xóa"

        if hanh_dong_popup == "ok":
            page.confirm_delete()
            WebDriverWait(logged_in_driver, 7).until(
                lambda d: page.get_cart_item_count() < count_before
                          or page.is_empty_cart_visible()
            )
            count_after = page.get_cart_item_count()
            assert count_after == count_before - 1 or page.is_empty_cart_visible(), \
                f"[{tc_id}] {mo_ta} | Trước: {count_before}, Sau: {count_after}"
        else:
            page.cancel_delete()
            WebDriverWait(logged_in_driver, 5).until(
                lambda d: not page.is_confirm_popup_visible()
            )
            count_after = page.get_cart_item_count()
            assert count_after == count_before, \
                f"[{tc_id}] {mo_ta} | SP phải vẫn còn. Trước: {count_before}, Sau: {count_after}"

    def test_remove_multiple_products(self, logged_in_driver):
       
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)

        so_sp  = REMOVE_MULTIPLE["so_sp_toi_thieu"]   # 3
        so_lan = REMOVE_MULTIPLE["so_lan_xoa"]         # 2

        actual = page.ensure_cart_has_n_products(base_url, n=so_sp)
        if actual < 2:
            pytest.skip(
                f"TC-22: Cần ≥ 2 SP trong giỏ để xóa, thêm được {actual} SP. "
                "Kiểm tra web có đủ SP khác nhau để thêm không."
            )

        count = page.get_cart_item_count()
        for i in range(so_lan):
            page.click_remove(index=0)
            WebDriverWait(logged_in_driver, 5).until(
                lambda d: page.is_confirm_popup_visible()
            )
            assert page.is_confirm_popup_visible(), \
                f"TC-22: Lần xóa thứ {i + 1} phải hiện popup 'Bạn có chắc chắn xóa sản phẩm này khỏi giỏ hàng'"
            page.confirm_delete()
            WebDriverWait(logged_in_driver, 7).until(
                lambda d: page.get_cart_item_count() == count - (i + 1)
                          or page.is_empty_cart_visible()
            )

        assert page.get_cart_item_count() == count - so_lan \
               or page.is_empty_cart_visible(), \
            f"TC-22: Sau {so_lan} lần xóa số SP phải giảm đúng " \
            f"(mong đợi {count - so_lan}, thực tế {page.get_cart_item_count()})"

    def test_remove_all_products(self, logged_in_driver):
        
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)

        so_sp = REMOVE_ALL["so_sp_toi_thieu"]   # 3

        actual = page.ensure_cart_has_n_products(base_url, n=so_sp)
        if actual == 0:
            pytest.skip(
                "TC-23: Không thể thêm SP – "
                "kiểm tra locator BTN_ADD_TO_CART và XPath SP trên trang chủ."
            )

        # Xóa từng SP cho đến khi giỏ rỗng
        while page.get_cart_item_count() > 0:
            count_before = page.get_cart_item_count()
            page.click_remove(index=0)
            WebDriverWait(logged_in_driver, 5).until(
                lambda d: page.is_confirm_popup_visible()
            )
            assert page.is_confirm_popup_visible(), \
                "TC-23: Mỗi lần xóa phải hiện popup 'Bạn có chắc chắn xóa sản phẩm này khỏi giỏ hàng'"
            page.confirm_delete()
            WebDriverWait(logged_in_driver, 7).until(
                lambda d: page.get_cart_item_count() < count_before
                          or page.is_empty_cart_visible()
            )

        assert page.is_empty_cart_visible(), \
            f"TC-23: Sau khi xóa hết phải hiện '{REMOVE_ALL['expected_text']}'"


# ==============================================================
# NHÓM 7: BIZ – Tiếp tục mua sắm  –  TC-33
# ==============================================================
class TestCartContinueShopping:

    def test_continue_shopping(self, logged_in_driver):
        """TC-25: Click TIẾP TỤC MUA SẮM → chuyển về trang chủ."""
        page = CartPage(logged_in_driver)
        page.open_cart(base_url)
        page.click_continue_shopping()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: "cart" not in d.current_url.lower()
                      and "order" not in d.current_url.lower()
        )
        assert "cart" not in logged_in_driver.current_url.lower(), \
            "TC-25: Sau khi click Tiếp tục mua sắm phải về trang chủ"