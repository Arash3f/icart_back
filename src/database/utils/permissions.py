from src.permission import permission_codes as permission
from src.permission.schema import PermissionCreate

permissions_in: list[PermissionCreate] = [
    # ! ROLE
    PermissionCreate(name="مشاهده نقش ها", code=permission.VIEW_ROLE),
    PermissionCreate(name="ساخت نقش", code=permission.CREATE_ROLE),
    PermissionCreate(name="ویرایش نقش", code=permission.UPDATE_ROLE),
    PermissionCreate(name="حذف نقش", code=permission.DELETE_ROLE),
    PermissionCreate(name="اختصاص نقش به کاربران", code=permission.ASSIGN_ROLE),
    # ! PERMISSIONS
    PermissionCreate(name="مشاهده دسترسی ها", code=permission.VIEW_PERMISSION),
    # ! USER_MESSAGE
    PermissionCreate(name="مشاهده پیام های کاربران", code=permission.VIEW_USER_MESSAGE),
    PermissionCreate(name="ارسال پیام به کاربر", code=permission.CREATE_USER_MESSAGE),
    PermissionCreate(
        name="ویرایش پیام های کاربران",
        code=permission.UPDATE_USER_MESSAGE,
    ),
    PermissionCreate(name="حذف پیام های کاربران", code=permission.DELETE_USER_MESSAGE),
    # ! NEWS
    PermissionCreate(name="ساخت خبر", code=permission.CREATE_NEWS),
    PermissionCreate(name="ویرایش اخبار", code=permission.UPDATE_NEWS),
    PermissionCreate(name="حذف اخبار", code=permission.DELETE_NEWS),
    # ! VERIFY_PHONE
    PermissionCreate(
        name="مشاهده کد های اعتبار سنجی موبایل",
        code=permission.VIEW_VERIFY_PHONE,
    ),
    # ! IMPORTANT_DATA
    PermissionCreate(name="مشاهده اطلاعات ساخت", code=permission.VIEW_IMPORTANT_DATA),
    PermissionCreate(name="ویرایش اطلاعات ساخت", code=permission.UPDATE_IMPORTANT_DATA),
    # ! FEE
    PermissionCreate(name="مشاهده کارمزد ها", code=permission.VIEW_FEE),
    PermissionCreate(name="ساخت کارمزد", code=permission.CREATE_FEE),
    PermissionCreate(name="ویرایش کارمزد", code=permission.UPDATE_FEE),
    PermissionCreate(name="حذف کارمزد", code=permission.DELETE_FEE),
    # ! TICKET
    PermissionCreate(name="مشاهده تیکت ها", code=permission.VIEW_TICKET),
    PermissionCreate(name="جواب دادن به تیکت", code=permission.RESPONSE_TICKET),
    # ! LOCATION
    PermissionCreate(name="مشاهده منطقه ها", code=permission.VIEW_LOCATION),
    PermissionCreate(name="ساخت منطقه", code=permission.CREATE_LOCATION),
    PermissionCreate(name="ویرایش منطقه", code=permission.UPDATE_LOCATION),
    # ! POS
    PermissionCreate(name="مشاهده پوز ها", code=permission.VIEW_POS),
    PermissionCreate(name="ساخت پوز", code=permission.CREATE_POS),
    PermissionCreate(name="ویرایش پوز", code=permission.UPDATE_POS),
    PermissionCreate(name="حذف پوز", code=permission.DELETE_POS),
    # ! CARD
    PermissionCreate(name="مشاهده کارت ها", code=permission.VIEW_CARD),
    # ! Crypto
    PermissionCreate(name="مشاهده کریپتو ها", code=permission.VIEW_CRYPTO),
    PermissionCreate(name="ساخت کریپتو", code=permission.CREATE_CRYPTO),
    PermissionCreate(name="ویرایش کریپتو", code=permission.UPDATE_CRYPTO),
    PermissionCreate(name="حذف کریپتو", code=permission.DELETE_CRYPTO),
    # ! UserCrypto
    PermissionCreate(name="مشاهده کریپتو کاربران", code=permission.VIEW_USER_CRYPTO),
    # ! Wallet
    PermissionCreate(name="مشاهده ولت کاربران", code=permission.VIEW_WALLET),
    # ! USER
    PermissionCreate(name="می تواند کاربران را ببیند", code=permission.VIEW_USER),
    PermissionCreate(name="می تواند کاربر اضافه کند", code=permission.CREATE_USER),
    PermissionCreate(
        name="می تواند کاربران را بروزرسانی کند",
        code=permission.UPDATE_USER,
    ),
    PermissionCreate(
        name="می تواند کاربران را غیر فعال کند",
        code=permission.DEACTIVATE_USER,
    ),
    # ! AGENT
    PermissionCreate(name="می تواند نماینده ها را ببیند", code=permission.VIEW_AGENT),
    PermissionCreate(name="می تواند نماینده اضافه کند", code=permission.CREATE_AGENT),
    PermissionCreate(
        name="می تواند نماینده ها را بروزرسانی کند",
        code=permission.UPDATE_AGENT,
    ),
    PermissionCreate(
        name="می تواند نماینده ها را حذف کند",
        code=permission.DELETE_AGENT,
    ),
    # ! ORGANIZATION
    PermissionCreate(
        name="می تواند سازمان ها را ببیند",
        code=permission.VIEW_ORGANIZATION,
    ),
    PermissionCreate(
        name="می تواند سازمان اضافه کند",
        code=permission.CREATE_ORGANIZATION,
    ),
    PermissionCreate(
        name="می تواند سازمان ها را بروزرسانی کند ",
        code=permission.UPDATE_ORGANIZATION,
    ),
    PermissionCreate(
        name="می تواند سازمان ها را حذف کند",
        code=permission.DELETE_ORGANIZATION,
    ),
    # ! CAPITAL TRANSFER
    PermissionCreate(
        name="می تواند انتقال ها را ببیند",
        code=permission.VIEW_CAPITAL_TRANSFER,
    ),
    PermissionCreate(
        name="می تواند انتقال ها را تایید کند ",
        code=permission.APPROVE_CAPITAL_TRANSFER,
    ),
    # ! POSITION REQUEST
    # ! ABILITY
    # ! AUTH
    # ! CONTRACT
    # ! CREDIT
    # ! IMPORTANT DATA
    # ! INVOICE
    # ! LOCATION
    # ! MERCHANT
    # ! NEWS
    # ! TERMINAL
    # ! TRANSACTION
    # ! USER
    # ! USER MESSAGE
    # ! VERIFY PHONE
    # ! WALLET
    # ! CRYPTO
    # ! USER TOKEN
    # ! TICKET
    # ! TICKET MESSAGE
    # ! POST
    # ! SITE MEDIA
]
