from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 31XX !
# !!!!!!!!!!!!!


class LogNotFoundException(HTTPException):
    """
    ? Exception When Log Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3100,
            "persian_message": "لاگ مورد نظر پیدا نشد!",
            "english_message": "Log Not Found!",
        }
        self.headers = None
