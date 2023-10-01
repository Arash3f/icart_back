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
        }
        self.headers = None
