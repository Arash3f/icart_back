from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 20XX !
# !!!!!!!!!!!!!


class UserCryptoNotFoundException(HTTPException):
    """
    ? Exception When UserCrypto Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2000,
            "persian_message": "کریپتو کاربر پیدا نشد!",
            "english_message": "User Crypto Not Found!",
        }
        self.headers = None
