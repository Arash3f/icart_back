from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 6XX !
# !!!!!!!!!!!!


class ContractNotFoundException(HTTPException):
    """
    ? Exception When Contract Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 600,
            "persian_message": "قرارداد مورد نظر پیدا نشد!",
            "english_message": "Contract Not Found!",
        }
        self.headers = None
