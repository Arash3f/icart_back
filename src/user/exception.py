import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 1XX !
# !!!!!!!!!!!!


class UserNotFoundException(HTTPException):
    """
    ? Exception When User Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 100,
            "english_message": "User not found!",
            "persian_message": "کاربر مورد نظر پیدا نشد!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class IncorrectUsernameOrPasswordException(HTTPException):
    """
    ? Exception When Username Or Password Is Incorrect
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 101,
            "english_message": "Incorrect username or password!",
            "persian_message": "نام کاربری یا رمز عبور اشتباه است!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class UsernameIsDuplicatedException(HTTPException):
    """
    ? Exception When Username Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 102,
            "english_message": "Username is duplicated!",
            "persian_message": "نام کاربری تکراری است!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class NationalCodeIsDuplicatedException(HTTPException):
    """
    ? Exception When National Code Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 103,
            "english_message": "National Code is duplicated!",
            "persian_message": "کد ملی تکراری است!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
