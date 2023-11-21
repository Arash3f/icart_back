import jdatetime
from fastapi import HTTPException


class InCorrectDataException(HTTPException):
    """
    ? Exception When Input data is incorrect
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1,
            "persian_message": "اطلاعات وارد شده نامعتبر است!",
            "english_message": "Input data is incorrect!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class TechnicalProblemException(HTTPException):
    """
    ? Exception When Technical Problem
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2,
            "persian_message": "مشکلی در بخش فنی پیش آمده است، لطفا با بخش فنی تماس بگیرید!",
            "english_message": "There is a problem in the technical department, please contact the technical department!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
