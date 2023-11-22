from fastapi import HTTPException


# ---------------------------------------------------------------------------
class WithdrawNotFound(HTTPException):
    def __init__(self):
        self.status_code = 404
        self.detail = {
            "code": 4400,
            "persian_message": "درخواست برداشت مورد نظر یافت نشد",
            "english_message": "Withdraw not found"
        }


# ---------------------------------------------------------------------------
class WithdrawOutOfAmount(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 4401,
            "persian_message": "مبلغ برداشت از موجودی نقدی حساب شما بیشتر است",
            "english_message": "Withdraw out of amount"
        }
