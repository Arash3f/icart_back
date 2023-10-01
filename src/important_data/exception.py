from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 9XX !
# !!!!!!!!!!!!!


class ImportantDataNotFoundException(HTTPException):
    """
    ? Exception When ImportantData Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 900,
            "persian_message": "داده مورد نظر پیدا نشد!",
            "english_message": "ImportantData Not Found!",
        }
        self.headers = None


class MaxImportantDataException(HTTPException):
    """
    ? Exception When can not create a new important data
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 901,
            "persian_message": "نمی توان داده ی جدید ساخت!",
            "english_message": "Can not create a new important data!",
        }
        self.headers = None
