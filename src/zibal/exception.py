import jdatetime
from fastapi import HTTPException


class InvalidBankCardException(HTTPException):
    """
    ? Exception When bank card is invalid
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 6600,
            "persian_message": "کارت بانکی استفاده شده نامعتبر است!",
            "english_message": "The bank card used is invalid!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
