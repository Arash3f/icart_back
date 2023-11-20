import jdatetime
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
            "time": str(jdatetime.datetime.now()),
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
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class LackOfMoneyException(HTTPException):
    """
    ? Exception when wallet's cache does not have enough money
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2205,
            "persian_message": "موجودی نقدی شما کم است!",
            "english_message": "Lack Of Money Exception!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class LockWalletException(HTTPException):
    """
    ? Exception when wallet is lock
    """

    def __init__(self, time: str = None):
        self.status_code = 400
        self.detail = {
            "code": 2206,
            "persian_message": "ولت شما غیر فعال است!",
            "english_message": "Wallet is locked!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class MerchantLackOfMoneyException(HTTPException):
    """
    ? Exception when wallet's cache does not have enough money
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2205,
            "persian_message": "موجودی نقدی پذیرنده کم است!",
            "english_message": "Merchant Lack Of Money Exception!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
