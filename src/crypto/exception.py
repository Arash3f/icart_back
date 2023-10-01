from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 35XX !
# !!!!!!!!!!!!!


class CryptoNotFoundException(HTTPException):
    """
    ? Exception When Crypto Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3500,
            "persian_message": "کریپتو مورد نظر پیدا نشد!",
            "english_message": "Crypto Not Found!",
        }
        self.headers = None


class CryptoNameIsDuplicatedException(HTTPException):
    """
    ? Exception When Crypto Name Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3501,
            "persian_message": "نام کریپتو تکراری است!",
            "english_message": "Crypto Name Is Duplicated!",
        }
        self.headers = None
