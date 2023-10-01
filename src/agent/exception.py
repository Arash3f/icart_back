from fastapi import HTTPException

# !!!!!!!!!!!!
# ! Code 4XX !
# !!!!!!!!!!!!


class AgentNotFoundException(HTTPException):
    """
    ? Exception When Agent Not Found
    """

    def __init__(self):
        self.status_code = 400
        self.detail = {
            "code": 400,
            "persian_message": "نماینده مورد نظر پیدا نشد!",
            "english_message": "Agent Not Found!",
        }
        self.headers = None
