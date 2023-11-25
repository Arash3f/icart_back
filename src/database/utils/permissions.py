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
    PermissionCreate(
        name="می تواند کاربران را بروزرسانی کند",
        code=permission.UPDATE_USER,
    ),
    PermissionCreate(
        name="می تواند وضعیت کاربران را تغییر دهد",
        code=permission.CHANGE_USER_ACTIVITY,
    ),
    PermissionCreate(
        name="می تواند وارد اکانت کاربران بشود",
        code=permission.LOGIN_AS_ADMIN,
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
    # ! AGENT ABILITY
    PermissionCreate(
        name="می تواند توانایی نماینده ها را ببیند",
        code=permission.VIEW_ABILITY,
    ),
    PermissionCreate(
        name="می تواند توانایی نماینده اضافه کند",
        code=permission.CREATE_ABILITY,
    ),
    PermissionCreate(
        name="می تواند توانایی نماینده ها را بروزرسانی کند",
        code=permission.UPDATE_ABILITY,
    ),
    PermissionCreate(
        name="می تواند توانایی نماینده ها را حذف کند",
        code=permission.DELETE_ABILITY,
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
    # ! CONTRACT
    PermissionCreate(
        name="می تواند قرارداد ها را ببیند",
        code=permission.VIEW_CONTRACT,
    ),
    # ! POSITION REQUEST
    PermissionCreate(
        name="می تواند درخواست های سمت اضافه کند",
        code=permission.CREATE_POSITION_REQUEST,
    ),
    PermissionCreate(
        name="می تواند درخواست های سمت را ببیند",
        code=permission.VIEW_POSITION_REQUEST,
    ),
    PermissionCreate(
        name="می تواند درخواست های سمت را تایید کند",
        code=permission.APPROVE_POSITION_REQUEST,
    ),
    PermissionCreate(
        name="می تواند درخواست های سمت را ویرایش کند",
        code=permission.UPDATE_POSITION_REQUEST,
    ),
    # ! USER REQUEST
    PermissionCreate(
        name="می تواند درخواست های کاربران را تایید کند",
        code=permission.APPROVE_USER_REQUEST,
    ),
    PermissionCreate(
        name="می تواند درخواست های کاربران را ببیند",
        code=permission.VIEW_USER_REQUEST,
    ),
    PermissionCreate(
        name="می تواند درخواست های کاربران را ویرایش کند",
        code=permission.UPDATE_USER_REQUEST,
    ),
    # ! VIEW_INSTALLMENTS
    PermissionCreate(
        name="می تواند اقساط را ببیند",
        code=permission.VIEW_INSTALLMENTS,
    ),
    # ! LOG
    PermissionCreate(
        name="می تواند لاگ های سیستم را ببیند",
        code=permission.VIEW_LOG,
    ),
    # ! MERCHANT
    PermissionCreate(
        name="می تواند پذیرنده ها را ببیند",
        code=permission.VIEW_MERCHANT,
    ),
    PermissionCreate(
        name="می تواند درصد سود پذیرنده ها را ویرایش کند",
        code=permission.UPDATE_MERCHANT,
    ),
    # ! TRANSACTION
    PermissionCreate(
        name="می تواند تراکنش ها را ببیند",
        code=permission.VIEW_TRANSACTION,
    ),
    # ! COOPERATION REQUEST
    PermissionCreate(
        name="مشاهده درخواست های همکاری",
        code=permission.VIEW_COOPERATION_REQUEST,
    ),
    PermissionCreate(
        name="ویرایش درخواست همکاری",
        code=permission.UPDATE_COOPERATION_REQUEST,
    ),
    PermissionCreate(
        name="حذف درخواست همکاری",
        code=permission.DELETE_COOPERATION_REQUEST,
    ),
    # ! WITHDRAW
    PermissionCreate(
        name="میتواند درخواست برداشت را ببیند",
        code=permission.VIEW_WITHDRAW,
    ),
    PermissionCreate(
        name="میتواند درخواست برداشت دهد",
        code=permission.CREATE_WITHDRAW,
    ),
    PermissionCreate(
        name="میتواند درخواست برداشت را به روز رسانی کند",
        code=permission.UPDATE_WITHDRAW,
    ),
    PermissionCreate(
        name="میتواند درخواست برداشت را بررسی کند",
        code=permission.VALIDATE_WITHDRAW,
    ),
    # ! BANK CARD
    PermissionCreate(
        name="میتواند کارت های بانکی را ببیند",
        code=permission.BANK_CARD_VIEW,
    ),
    # ! DEPOSIT
    PermissionCreate(
        name="میتواند واریز پول را ببیند",
        code=permission.DEPOSIT_VIEW,
    ),
]
