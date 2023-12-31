from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 2XX !
# !!!!!!!!!!!!


class IncorrectUsernameOrPasswordException(HTTPException):
    """
    ? Exception When Username Or Password Is Incorrect
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 200,
            "english_message": "Incorrect username or password!",
            "persian_message": "نام کاربری یا رمز عبور اشتباه است!",
        }
        self.headers = None


class InactiveUserException(HTTPException):
    """
    ? Exception When User is Inactive
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 203,
            "english_message": "User Is Inactive!",
            "persian_message": "کاربر مورد نظر غیر فعال است!",
        }
        self.headers = None


class IncorrectVerifyCodeException(HTTPException):
    """
    ? Exception When Verify Code is Incorrect
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 204,
            "english_message": "Verify Code Is Incorrect!",
            "persian_message": "کد فعال سازی نامعتبر است!",
        }
        self.headers = None


class AccessDeniedException(HTTPException):
    """
    ? User does not have the access permission
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 205,
            "english_message": "Access Denied Exception!",
            "persian_message": "دسترسی داده نشده است!",
        }
        self.headers = None


class UserNotAuthenticatedException(HTTPException):
    """
    ? Exception When User not authenticated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 206,
            "english_message": "User Is Not Authenticated!",
            "persian_message": "ابتدا وارد شوید!",
        }
        self.headers = None
