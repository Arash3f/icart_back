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
            "persian_message": "انقال مورد نظر پیدا نشد!",
            "english_message": "CapitalTransfer Not Found!",
        }
        self.headers = None
