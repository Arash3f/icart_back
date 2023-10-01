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
        }
        self.headers = None
