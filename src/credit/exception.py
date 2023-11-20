import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 7XX !
# !!!!!!!!!!!!


class CreditNotFoundException(HTTPException):
    """
    ? Exception When Credit Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 700,
            "persian_message": "اعتبار مورد نظر پیدا نشد!",
            "english_message": "Credit Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
