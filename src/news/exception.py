import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 26XX !
# !!!!!!!!!!!!!


class NewsNotFoundException(HTTPException):
    """
    ? Exception When News Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2600,
            "persian_message": "اخبار مورد نظر پیدا نشد!",
            "english_message": "News Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
