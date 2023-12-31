from src.location.schema import LocationInitCreate

location_in: list[LocationInitCreate] = [
    LocationInitCreate(name="فارس", parent_name=None),
    LocationInitCreate(name="شیراز", parent_name="فارس"),
    LocationInitCreate(name="مرودشت", parent_name="فارس"),
    LocationInitCreate(name="جهرم", parent_name="فارس"),
    LocationInitCreate(name="فسا", parent_name="فارس"),
    LocationInitCreate(name="کازرون", parent_name="فارس"),
    LocationInitCreate(name="صدرا", parent_name="فارس"),
    LocationInitCreate(name="داراب", parent_name="فارس"),
    LocationInitCreate(name="فیروزآباد", parent_name="فارس"),
    LocationInitCreate(name="آباده", parent_name="فارس"),
    LocationInitCreate(name="ارسنجان", parent_name="فارس"),
    LocationInitCreate(name="نورآباد", parent_name="فارس"),
    LocationInitCreate(name="نی‌ریز", parent_name="فارس"),
    LocationInitCreate(name="اقلید", parent_name="فارس"),
    LocationInitCreate(name="استهبان", parent_name="فارس"),
    LocationInitCreate(name="ارسنجان", parent_name="فارس"),
    LocationInitCreate(name="اوز", parent_name="فارس"),
    LocationInitCreate(name="بختگان", parent_name="فارس"),
    LocationInitCreate(name="بوانات", parent_name="فارس"),
    LocationInitCreate(name="پاسارگاد", parent_name="فارس"),
    LocationInitCreate(name="جویم", parent_name="فارس"),
    LocationInitCreate(name="خرامه", parent_name="فارس"),
    LocationInitCreate(name="خرم‌بید", parent_name="فارس"),
    LocationInitCreate(name="خفر", parent_name="فارس"),
    LocationInitCreate(name="خنج", parent_name="فارس"),
    LocationInitCreate(name="رستم", parent_name="فارس"),
    LocationInitCreate(name="بیضا", parent_name="فارس"),
    LocationInitCreate(name="زرین ‌دشت", parent_name="فارس"),
    LocationInitCreate(name="سپیدان", parent_name="فارس"),
    LocationInitCreate(name="سرچهان", parent_name="فارس"),
    LocationInitCreate(name="سروستان", parent_name="فارس"),
    LocationInitCreate(name="فراشبند", parent_name="فارس"),
    LocationInitCreate(name="کوار", parent_name="فارس"),
    LocationInitCreate(name="کوه‌چنار", parent_name="فارس"),
    LocationInitCreate(name="گراش", parent_name="فارس"),
    LocationInitCreate(name="لارستان", parent_name="فارس"),
    LocationInitCreate(name="لامرد", parent_name="فارس"),
    LocationInitCreate(name="مرکزی", parent_name=None),
    LocationInitCreate(name="اراک", parent_name="مرکزی"),
    LocationInitCreate(name="ساوه", parent_name="مرکزی"),
    LocationInitCreate(name="خمین", parent_name="مرکزی"),
    LocationInitCreate(name="محلات", parent_name="مرکزی"),
    LocationInitCreate(name="دلیجان", parent_name="مرکزی"),
    LocationInitCreate(name="کرهرود", parent_name="مرکزی"),
    LocationInitCreate(name="شازند", parent_name="مرکزی"),
    LocationInitCreate(name="مأمونیه", parent_name="مرکزی"),
    LocationInitCreate(name="تفرش", parent_name="مرکزی"),
    LocationInitCreate(name="مهاجران", parent_name="مرکزی"),
    LocationInitCreate(name="سنجان", parent_name="مرکزی"),
    LocationInitCreate(name="کمیجان", parent_name="مرکزی"),
    LocationInitCreate(name="آشتیان", parent_name="مرکزی"),
    LocationInitCreate(name="خنداب", parent_name="مرکزی"),
    LocationInitCreate(name="آستانه", parent_name="مرکزی"),
    LocationInitCreate(name="پرندک", parent_name="مرکزی"),
    LocationInitCreate(name="زاویه", parent_name="مرکزی"),
    LocationInitCreate(name="نیمور", parent_name="مرکزی"),
    LocationInitCreate(name="داودآباد", parent_name="مرکزی"),
    LocationInitCreate(name="غرق آباد", parent_name="مرکزی"),
    LocationInitCreate(name="خشکرود", parent_name="مرکزی"),
    LocationInitCreate(name="میلاجرد", parent_name="مرکزی"),
    LocationInitCreate(name="جاورسیان", parent_name="مرکزی"),
    LocationInitCreate(name="فرمهین", parent_name="مرکزی"),
    LocationInitCreate(name="ساروق", parent_name="مرکزی"),
    LocationInitCreate(name="کارچان", parent_name="مرکزی"),
    LocationInitCreate(name="نراق", parent_name="مرکزی"),
    LocationInitCreate(name="توره", parent_name="مرکزی"),
    LocationInitCreate(name="نوبران", parent_name="مرکزی"),
    LocationInitCreate(name="هندودر", parent_name="مرکزی"),
    LocationInitCreate(name="قورچی باشی", parent_name="مرکزی"),
    LocationInitCreate(name="رازقان", parent_name="مرکزی"),
    LocationInitCreate(name="شهباز", parent_name="مرکزی"),
    LocationInitCreate(name="کرمان", parent_name=None),
    LocationInitCreate(name="کرمان", parent_name="کرمان"),
    LocationInitCreate(name="بم", parent_name="کرمان"),
    LocationInitCreate(name="سیرجان", parent_name="کرمان"),
    LocationInitCreate(name="رفسنجان", parent_name="کرمان"),
    LocationInitCreate(name="جیرفت", parent_name="کرمان"),
    LocationInitCreate(name="بافت", parent_name="کرمان"),
    LocationInitCreate(name="زرند", parent_name="کرمان"),
    LocationInitCreate(name="شهربابک", parent_name="کرمان"),
    LocationInitCreate(name="بردسیر", parent_name="کرمان"),
    LocationInitCreate(name="کهنوج", parent_name="کرمان"),
    LocationInitCreate(name="راور", parent_name="کرمان"),
    LocationInitCreate(name="منوجان", parent_name="کرمان"),
    LocationInitCreate(name="عنبرآباد", parent_name="کرمان"),
    LocationInitCreate(name="کوهبنان", parent_name="کرمان"),
    LocationInitCreate(name="رودبار جنوب", parent_name="کرمان"),
    LocationInitCreate(name="قلعه گنج", parent_name="کرمان"),
    LocationInitCreate(name="ریگان", parent_name="کرمان"),
    LocationInitCreate(name="فهرج", parent_name="کرمان"),
    LocationInitCreate(name="انار", parent_name="کرمان"),
    LocationInitCreate(name="رابر", parent_name="کرمان"),
    LocationInitCreate(name="نرماشیر", parent_name="کرمان"),
    LocationInitCreate(name="ارزوئیه", parent_name="کرمان"),
    LocationInitCreate(name="فاریاب", parent_name="کرمان"),
    LocationInitCreate(name="جازموریان", parent_name="کرمان"),
    LocationInitCreate(name="گنبکی", parent_name="کرمان"),
]
