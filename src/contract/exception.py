import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 6XX !
# !!!!!!!!!!!!


class ContractNotFoundException(HTTPException):
    """
    ? Exception When Contract Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 600,
            "persian_message": "قرارداد مورد نظر پیدا نشد!",
            "english_message": "Contract Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class ContractNumberIsDuplicatedException(HTTPException):
    """
    ? Exception When Contract number is duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 601,
            "persian_message": "شماره قرارداد تکراری است!",
            "english_message": "Contract Number Is Duplicated!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
