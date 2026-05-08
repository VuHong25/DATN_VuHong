 

login_data = [

    ("DN-blank-user-TC7", "", "123456789", "html5"),
    ("DN-wrong-user-TC8", "tets_1", "123456789", "Tài khoản hoặc mật khẩu không đúng!"),
    ("DN-not-exist-TC9", "haha", "123456789", "Tài khoản hoặc mật khẩu không đúng!"),
    ("DN-case-sens-TC10", "Test_1", "123456789", "Tài khoản hoặc mật khẩu không đúng!"),
    ("DN-valid-TC11", "test_1", "123456789", "success"),
    ("DN-blank-pass-TC12", "test_1", "", "html5"),
    ("DN-wrong-pass-TC13", "test_1", "wrongpass", "Tài khoản hoặc mật khẩu không đúng!"),
    ("DN-valid-TC14", "test_1", "123456789", "success"),
]

    # ("DN-valid-15", "test_1", "123456789", "success"),
    # ("DN-disabled-TC16", "a", "123456789", "Tài khoản của bạn đã bị vô hiệu hóa !"),
# ]