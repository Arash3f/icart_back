from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 22XX !
# !!!!!!!!!!!!!


class WalletNotFoundException(HTTPException):
    """
    ? Exception When Wallet Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2201,
            "persian_message": "ولت مورد نظر پیدا نشد!",
            "english_message": "Wallet Not Found!",
        }
        self.headers = None


class LackOfCreditException(HTTPException):
    """
    ? Exception when wallet's credit does not have enough money
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2204,
            "persian_message": "موجودی اعتباری شما کم است!",
            "english_message": "Lack Of Credit Exception!",
        }
        self.headers = None


class LackOfMoneyException(HTTPException):
    """
    ? Exception when wallet's cache does not have enough money
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 2205,
            "persian_message": "موجودی نقدی شما کم است!",
            "english_message": "Lack Of Money Exception!",
            "time": time,
        }
        self.headers = None
