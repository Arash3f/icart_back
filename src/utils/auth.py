import requests

from src.core.config import settings

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

    if res["data"]:
        if res["data"]["matched"]:
            if (
                res["data"]["firstName"] == request_first_name
                and res["data"]["lastName"] == request_last_name
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

    if res["data"]:
        if res["data"]["matched"]:
            return True

    return False
