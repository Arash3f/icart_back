import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 25XX !
# !!!!!!!!!!!!!


class PermissionNotFoundException(HTTPException):
    """
    ? Exception When Permission Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2500,
            "persian_message": "دسترسی مورد نظر پیدا نشد!",
            "english_message": "Permission Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
