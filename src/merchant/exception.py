import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 12XX !
# !!!!!!!!!!!!!


class MerchantNotFoundException(HTTPException):
    """
    ? Exception When merchant Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1200,
            "persian_message": "پذیرنده مورد نظر پیدا نشد!",
            "english_message": "merchant Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
