from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 51XX !
# !!!!!!!!!!!!!


class CooperationRequestNotFoundException(HTTPException):
    """
    ? Exception When Location Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 5100,
            "persian_message": "درخواست همکاری مورد نظر پیدا نشد!",
            "english_message": "Cooperation Request Not Found!",
        }
        self.headers = None
