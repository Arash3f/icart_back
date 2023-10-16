from enum import Enum
from random import randint


class CardType(Enum):
    Credit = "1"
    Swipe = "2"


class CreditType(Enum):
    Rial = "1"
    Currency = "2"
    Dollar = "3"
    Yuan = "4"


class CompanyType(Enum):
    Icart = "100"
    Fafa = "200"


def generate_card_number(
    card_type: CardType,
    credit_type: CreditType,
    company_type: CompanyType,
):
    card_number = "17"
    card_number += card_type.value
    card_number += credit_type.value
    card_number += str(randint(1000000, 9999999))
    card_number += company_type.value

    # ! Calculate Checksum digit
    sum_dig = 0
    for i in card_number:
        buf = str(int(i) * 2)
        if len(buf) > 1:
            buf = int(buf[0]) + int(buf[1])

        sum_dig += int(buf)

    checksum_digit = 10 - (sum_dig - (sum_dig // 10) * 10)
    if checksum_digit == 10:
        checksum_digit = 0

    card_number += str(checksum_digit)
    return card_number