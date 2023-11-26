import requests

from src.core.config import settings
from src.user.models import User

token = settings.KAVENEGAR_TOKEN
auth_token = "Bearer d3309a731ef64381be20a6a564ede39c"
base_url = "https://api.kavenegar.com/v1/{}/verify/lookup.json?".format(token)


def national_identity_inquiry(
    natioal_code: str,
    birth_date: str,
    request_first_name: str,
    request_last_name: str,
) -> bool:
    res = requests.post(
        url="https://api.zibal.ir/v1/facility/nationalIdentityInquiry/",
        headers={
            "Authorization": auth_token,
        },
        json={
            "nationalCode": natioal_code,
            "birthDate": birth_date,
        },
    )

    res = res.json()

    if res["result"] == 1:
        if res["data"]:
            if res["data"]["matched"]:
                if (
                    request_first_name.replace(" ", "") in res["data"]["firstName"]
                    and request_last_name.replace(" ", "") in res["data"]["lastName"]
                ):
                    return True

    return False


def shahkar_inquiry(
    national_code: str,
    mobile: str,
) -> bool:
    res = requests.post(
        url="https://api.zibal.ir/v1/facility/shahkarInquiry",
        headers={
            "Authorization": auth_token,
        },
        json={
            "nationalCode": national_code,
            "mobile": mobile,
        },
    )

    res = res.json()

    if res["result"] == 1:
        if res["data"]:
            if res["data"]["matched"]:
                return True

    return False


def verify_bank_card(
    user: User,
    card_number: str,
    shaba_number: str,
) -> bool:
    res = requests.post(
        url="https://api.zibal.ir/v1/facility/cardToIban",
        headers={
            "Authorization": auth_token,
        },
        json={
            "cardNumber": card_number,
        },
    )

    res = res.json()

    if res["result"] == 1:
        if res["data"] and res["message"] == "موفق":
            name = "{} {}".format(user.first_name, user.last_name)
            check_name = name in res["data"]["name"]
            check_shaba_number = shaba_number == res["data"]["IBAN"]
            if check_name and check_shaba_number:
                return True

    return False
