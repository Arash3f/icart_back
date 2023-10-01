from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 13XX !
# !!!!!!!!!!!!!


class OrganizationNotFoundException(HTTPException):
    """
    ? Exception When Organization Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1300,
            "persian_message": "سازمان مورد نظر پیدا نشد!",
            "english_message": "Organization Not Found!",
        }
        self.headers = None
