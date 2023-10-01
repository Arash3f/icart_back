from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 24XX !
# !!!!!!!!!!!!!


class TransactionNotFoundException(HTTPException):
    """
    ? Exception when transaction not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2400,
            "persian_message": "اطلاعات پرداخت مورد نظر پیدا نشد!",
            "english_message": "Transaction Not Found!",
        }
        self.headers = None
