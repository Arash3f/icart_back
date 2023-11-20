import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 3XX !
# !!!!!!!!!!!!


class AbilityNotFoundException(HTTPException):
    """
    ? Exception When Ability Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 300,
            "persian_message": "توانایی مورد نظر پیدا نشد!",
            "english_message": "Ability Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class AbilityNameIsDuplicatedException(HTTPException):
    """
    ? Exception When Ability Name Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 301,
            "persian_message": "نام وارد شده تکراری است!",
            "english_message": "Ability Name Is Duplicated!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
