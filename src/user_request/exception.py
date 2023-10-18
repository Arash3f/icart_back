from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 30XX !
# !!!!!!!!!!!!!


class UserRequestNotFoundException(HTTPException):
    """
    ? Exception When User Request Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3000,
            "english_message": "User request not found!",
            "persian_message": "درخواست کاربر مورد نظر پیدا نشد!",
        }
        self.headers = None
