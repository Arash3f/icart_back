from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 3XX !
# !!!!!!!!!!!!


class AbilityNotFoundException(HTTPException):
    """
    ? Exception When Ability Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 300,
            "persian_message": "توانایی مورد نظر پیدا نشد!",
            "english_message": "Ability Not Found!",
        }
        self.headers = None


class AbilityNameIsDuplicatedException(HTTPException):
    """
    ? Exception When Ability Name Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 301,
            "persian_message": "نام وارد شده تکراری است!",
            "english_message": "Ability Name Is Duplicated!",
        }
        self.headers = None


class CanNotUpdateBaseAbilityException(HTTPException):
    """
    ? Exception When user want to update base ability
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 301,
            "persian_message": "نمی توان توانایی از پیش تعریف شده را ویرایش کرد!",
            "english_message": "Can Not Update Base Ability!",
        }
        self.headers = None
