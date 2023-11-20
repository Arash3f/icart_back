import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 20XX !
# !!!!!!!!!!!!!


class UserMessageNotFoundException(HTTPException):
    """
    ? Exception When UserMessage Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2001,
            "persian_message": "اطلاعات پیام مورد نظر پیدا نشد!",
            "english_message": "User Message Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
