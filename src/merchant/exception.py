from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 12XX !
# !!!!!!!!!!!!!


class MerchantNotFoundException(HTTPException):
    """
    ? Exception When merchant Not Found
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 1200,
            "persian_message": "پذیرنده مورد نظر پیدا نشد!",
            "english_message": "merchant Not Found!",
            "time": time,
        }
        self.headers = None
