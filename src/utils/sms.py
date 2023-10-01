from datetime import datetime

import requests

from src.core.config import settings

token = settings.KAVENEGAR_TOKEN
base_url = "https://api.kavenegar.com/v1/{}/verify/lookup.json?".format(token)


def send_dynamic_password_sms(
    phone_number: str,
    dynamic_password: int,
    exp_time: datetime,
) -> bool:
    """
    ! Send dynamic password

    Parameters
    ----------
    phone_number
        User phone number
    dynamic_password
        User dynamic password
    exp_time
        Dynamic password exp time

    Returns
    -------
    res
        result of operation
    """
    receptor = phone_number
    token = dynamic_password
    token2 = exp_time
    template = "dynami-password"

    url = base_url + "receptor={}&token={}&token2={}&template={}".format(
        receptor,
        token,
        token2,
        template,
    )
    requests.get(url)
    return True


def send_decrease_money_sms(
    phone_number: str,
    user_card_number: str,
    amount: int,
    current_money: int,
) -> bool:
    """
    ! Send decrease money from card

    Parameters
    ----------
    phone_number
        User phone number
    user_card_number
        User card number
    amount
    current_money

    Returns
    -------
    res
        result of operation
    """
    receptor = phone_number
    token = user_card_number
    token2 = amount
    token3 = current_money
    template = "decrease-money"

    url = base_url + "receptor={}&token={}&token2={}&token3{}&template={}".format(
        receptor,
        token,
        token2,
        token3,
        template,
    )
    requests.get(url)
    return True


def send_verify_phone_sms(
    phone_number: str,
    code: int,
) -> bool:
    """
    ! Send verify phone code

    Parameters
    ----------
    phone_number
        User phone number
    code
        Phone verify code

    Returns
    -------

    """
    receptor = phone_number
    template = "verify-phone"

    url = base_url + "receptor={}&token={}&template={}".format(receptor, code, template)
    requests.get(url)
    return True
