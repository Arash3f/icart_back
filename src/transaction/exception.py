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


class TransactionLimitException(HTTPException):
    """
    ? Exception when Reached to Transaction's Limit
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 2401,
            "persian_message": "شما به سقف تراکنش های خود رسیده اید!",
            "english_message": "You Have Reached Your Transaction Limit!",
            "time": time,
        }
        self.headers = Nonene
