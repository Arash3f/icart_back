from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 23XX !
# !!!!!!!!!!!!!


class TicketNotFoundException(HTTPException):
    """
    ? Exception When Ticket Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2300,
            "persian_message": "تیکت مورد نظر پیدا نشد!",
            "english_message": "Ticket Not Found!",
        }
        self.headers = None


class TicketClosePositionException(HTTPException):
    """
    ? Exception When Ticket position is Close
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 2301,
            "persian_message": "تیکت مورد نظر بسته شده است!",
            "english_message": "Ticket position is Closed!",
        }
        self.headers = None
