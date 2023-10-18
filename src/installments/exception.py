from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 31XX !
# !!!!!!!!!!!!!


class InstallmentsNotFoundException(HTTPException):
    """
    ? Exception when Installments not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 3100,
            "persian_message": "قسط مورد نظر پیدا نشد!",
            "english_message": "Installments Not Found!",
        }
        self.headers = None
