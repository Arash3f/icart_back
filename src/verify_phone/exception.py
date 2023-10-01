from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 29XX !
# !!!!!!!!!!!!!


class VerifyPhoneNotFoundException(HTTPException):
    """
    ? Exception When Verify Phone Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2900,
            "persian_message": "اطلاعات پیامک مورد نظر پیدا نشد!",
            "english_message": "Verify Phone Not Found!",
        }
        self.headers = None
