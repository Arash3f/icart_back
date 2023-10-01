from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 27XX !
# !!!!!!!!!!!!!


class TerminalNotFoundException(HTTPException):
    """
    ? Exception when terminal not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2700,
            "persian_message": "ترمینال مورد نظر پیدا نشد!",
            "english_message": "Terminal Is not found!",
        }
        self.headers = None
