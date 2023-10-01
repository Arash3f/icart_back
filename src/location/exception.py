from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 11XX !
# !!!!!!!!!!!!!


class LocationParentNotFoundException(HTTPException):
    """
    ? Exception When Location parent Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1100,
            "persian_message": "منطقه والد پیدا نشد!",
            "english_message": "Location Parent Not Found!",
        }
        self.headers = None


class LocationNotFoundException(HTTPException):
    """
    ? Exception When Location Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1101,
            "persian_message": "منطقه مورد نظر پیدا نشد!",
            "english_message": "Location Not Found!",
        }
        self.headers = None


class LocationNameIsDuplicatedException(HTTPException):
    """
    ? Exception When Location Name Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1102,
            "persian_message": "نام منطقه تکراری است!",
            "english_message": "Location Name Is Duplicated!",
        }
        self.headers = None


class LocationHaveChildException(HTTPException):
    """
    ? Exception When Location Have Child
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1102,
            "persian_message": "منطقه مورد نظر دارای زیر منطقه است!",
            "english_message": "Location Have Child!",
        }
        self.headers = None
