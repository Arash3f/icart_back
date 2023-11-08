from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 77XX !
# !!!!!!!!!!!!!


class CashNotFoundException(HTTPException):
    """
    ? Exception When Cash Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 7700,
            "persian_message": "کیف پول مورد نظر پیدا نشد!",
            "english_message": "Cash Not Found!",
        }
        self.headers = None
