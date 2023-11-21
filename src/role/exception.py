import jdatetime
from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 16XX !
# !!!!!!!!!!!!!


class RoleNotFoundException(HTTPException):
    """
    ? Exception When Role Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1600,
            "persian_message": "رول مورد نظر پیدا نشد!",
            "english_message": "Role Not Found!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class RoleNameIsDuplicatedException(HTTPException):
    """
    ? Exception When Role Name Is Duplicated
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1601,
            "persian_message": "نام رول تکراری است!",
            "english_message": "Role Name Is Duplicated!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class RoleHaveUserException(HTTPException):
    """
    ? Exception When Role have user and can not delete
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1602,
            "persian_message": "نمی توان رول داری کاربر را پاک کرد!",
            "english_message": "Cannot delete the role that have user!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None


class CanNotChantUserWithMainRole(HTTPException):
    """
    ? Exception When change user with main role
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1603,
            "persian_message": "نمی توان کاربر با نقش اصلی را تغییر داد!",
            "english_message": "Cannot change user with main role!",
            "time": str(jdatetime.datetime.now()),
        }
        self.headers = None
