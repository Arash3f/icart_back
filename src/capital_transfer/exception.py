from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 5XX !
# !!!!!!!!!!!!


class CapitalTransferNotFoundException(HTTPException):
    """
    ? Exception When CapitalTransfer Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 500,
            "persian_message": "اننقال مورد نظر پیدا نشد!",
            "english_message": "CapitalTransfer Not Found!",
        }
        self.headers = None


class CapitalTransferFinishException(HTTPException):
    """
    ? Exception When CapitalTransfer is finish
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 501,
            "persian_message": "اننقال مورد نظر قبلا به اتمام رسیده است!",
            "english_message": "CapitalTransfer is finished!",
        }
        self.headers = None
