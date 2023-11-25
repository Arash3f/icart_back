import jdatetime
from fastapi import HTTPException


# ---------------------------------------------------------------------------
class DepositNotFound(HTTPException):
    def __init__(self):
        self.status_code = 404
        self.detail = {
            "code": 4400,
            "persian_message": "درخواست واریز مورد نظر یافت نشد",
            "english_message": "Deposit not found",
            "time": str(jdatetime.datetime.now()),
        }
