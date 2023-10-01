from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 30XX !
# !!!!!!!!!!!!!


class PosNotFoundException(HTTPException):
    """
    ? Exception when pos not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3000,
            "persian_message": "پوز مورد نظر پیدا نشد!",
            "english_message": "Pos Not Found!",
        }
        self.headers = None


class PosTokenIsDuplicatedException(HTTPException):
    """
    ? Exception when pos's token is duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3001,
            "persian_message": "توکن پوز تکراری است!",
            "english_message": "Pos Token Is Duplicated!",
        }
        self.headers = None
