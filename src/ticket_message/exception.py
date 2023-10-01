from fastapi import HTTPException

# !!!!!!!!!!!!!
# ! Code 15XX !
# !!!!!!!!!!!!!


class TicketMessageNotFoundException(HTTPException):
    """
    ? Exception When Ticket Message Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 1500,
            "persian_message": "پیام تیکت مورد نظر پیدا نشد!",
            "english_message": "Ticket Message Not Found!",
        }
        self.headers = None
