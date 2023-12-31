from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 8XX !
# !!!!!!!!!!!!!


class FeeNotFoundException(HTTPException):
    """
    ? Exception when fee not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 800,
            "persian_message": "کارمزد مورد نظر پیدا نشد!",
            "english_message": "Fee Not Found!",
        }
        self.headers = None


class FeeLimitIsDuplicatedException(HTTPException):
    """
    ? Exception when fee's limit is duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 801,
            "persian_message": "سقف کارمزد تکراری است!",
            "english_message": "Fee Limit Is Duplicated!",
        }
        self.headers = None


class InValidPercentageException(HTTPException):
    """
    ? Exception when fee's percentage is invalid
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 802,
            "persian_message": "درصد کارمزد معتبر نیست!",
            "english_message": "Fee's Percentage Is Invalid!",
        }
        self.headers = None
