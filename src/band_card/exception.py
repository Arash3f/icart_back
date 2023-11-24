import jdatetime
from fastapi import HTTPException


# -------------------------------------------------------------
class BankCardNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = 404
        self.detail = {
            "code": 3300,
            "persian_message": "کارت بانکی مورد نظر پیدا نشد!",
            "english_message": "Bank Card Not Found!",
            "time": str(jdatetime.datetime.now()),
        }


# -------------------------------------------------------------
class BankCardDuplicate(HTTPException):
    def __init__(self) -> None:
        self.status_code = 400
        self.detail = {
            "code": 3301,
            "persian_message": "کارت بانکی تکراری است",
            "english_message": "Bank Card duplicated",
            "time": str(jdatetime.datetime.now()),
        }


# -------------------------------------------------------------
class InValidBankCard(HTTPException):
    def __init__(self) -> None:
        self.status_code = 400
        self.detail = {
            "code": 3301,
            "persian_message": "کارت بانکی نامعتبر است",
            "english_message": "Invalid Bank Card",
            "time": str(jdatetime.datetime.now()),
        }
