from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 14XX !
# !!!!!!!!!!!!!


class PositionRequestNotFoundException(HTTPException):
    """
    ? Exception When PositionRequest Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1400,
            "persian_message": "درخواست مورد نظر پیدا نشد!",
            "english_message": "PositionRequest Not Found!",
        }
        self.headers = None


class ApproveAccessDeniedException(HTTPException):
    """
    ? Exception When
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1401,
            "persian_message": "شما اجازه تایید درخواست را ندارید!",
            "english_message": "You are not allowed to approve the request!",
        }
        self.headers = None
