from fastapi import HTTPException


# !!!!!!!!!!!!!
# ! Code 32XX !
# !!!!!!!!!!!!!


class CardNotFoundException(HTTPException):
    """
    ? Exception when card not found
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 3200,
            "persian_message": "کارت مورد نظر پیدا نشد!",
            "english_message": "Card Not Found!",
            "time": time,
        }
        self.headers = None


class UserCardDuplicateException(HTTPException):
    """
    ? Exception when user card duplicate
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 3201,
            "persian_message": "کارت مورد نظر شما تکراری است!",
            "english_message": "User Card Duplicate!",
            "time": time,
        }
        self.headers = None
