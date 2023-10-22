from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 30XX !
# !!!!!!!!!!!!!


class PosNotFoundException(HTTPException):
    """
    ? Exception when pos not found
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 3000,
            "persian_message": "پوز مورد نظر پیدا نشد!",
            "english_message": "Pos Not Found!",
            "time": time,
        }
        self.headers = None


class PosNumberIsDuplicatedException(HTTPException):
    """
    ? Exception when pos's number is duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3001,
            "persian_message": "توکن پوز تکراری است!",
            "english_message": "Pos Number Is Duplicated!",
        }
        self.headers = None
