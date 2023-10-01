from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 10XX !
# !!!!!!!!!!!!!


class InvoiceNotFoundException(HTTPException):
    """
    ? Exception when Invoice not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1000,
            "persian_message": "فاکتور مورد نظر پیدا نشد!",
            "english_message": "Invoice Not Found!",
        }
        self.headers = None


class InvoiceCannotDeletedException(HTTPException):
    """
    ? Exception when Invoice not found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1001,
            "persian_message": "نمی توان فاکتور مورد نظر را پاک کرد!",
            "english_message": "Can not Delete Invoice!",
        }
        self.headers = None
