import jdatetime
from fastapi import HTTPException


# !!!!!!!!!!!!!
# ! Code 32XX !
# !!!!!!!!!!!!!


class CardNotFoundException(HTTPException):
    """
    ? Exception when card not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3200,
            "persian_message": "کارت مورد نظر پیدا نشد!",
            "english_message": "Card Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class CardPasswordInValidException(HTTPException):
    """
    ? Exception when card password is invalid
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3202,
            "persian_message": "رمز کارت اشتباه است!",
            "english_message": "Card Password is Invalid!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class UserCardDuplicateException(HTTPException):
    """
    ? Exception when user card duplicate
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3201,
            "persian_message": "کارت مورد نظر شما تکراری است!",
            "english_message": "User Card Duplicate!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class UserCardIsDeActiveException(HTTPException):
    """
    ? Exception when user card is deactivate
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3201,
            "persian_message": "کارت غیر فعال است!",
            "english_message": "User Card Is Deactivate!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
