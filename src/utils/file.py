from random import randint
from uuid import UUID

import openpyxl
from sqlalchemy.ext.asyncio import AsyncSession

from src.cash.models import Cash
from src.credit.models import Credit
from src.location.crud import location as location_crud
from src.user.crud import user as user_crud
from src.organization.crud import organization as organization_crud
from src.user.models import User
from src.wallet.models import Wallet

dataframe = openpyxl.load_workbook("icart-register.xlsx")

dataframe1 = dataframe.active


async def read_excel_file(db: AsyncSession, user_id: UUID):
    organization_user = await organization_crud.find_by_user_id(
        db=db,
        user_id=user_id,
    )

    error_message: list[str] = []
    result_message: list[str] = []

    # ? Calculate all rows
    row_count = 0
    finish = False
    row = 2
    while not finish:
        for col in dataframe1.iter_cols(1, 1):
            if col[row].value:
                row_count += 1
            else:
                finish = True
        row += 1

    for row in dataframe1.iter_rows(3, row_count + 2):
        username = str(row[4].value)
        if len(username) != 11:
            text = "کاربر با شماره {} به دلیل پیدا نشدن منطقه وارد شده ({}) ثبت نشد! \n ".format(
                row[0].value,
                row[8].value,
            )
            error_message.append(text)

        else:
            # ! find location
            location = await location_crud.find_by_name(db=db, name=row[8].value)

            if not location:
                text = "کاربر با شماره {} به دلیل پیدا نشدن منطقه وارد شده ({}) ثبت نشد! \n ".format(
                    row[0].value,
                    row[8].value,
                )
                error_message.append(text)

            else:
                # * Check user not exist
                exist_user = await user_crud.check_by_username_and_national_code(
                    db=db,
                    username=str(row[4].value),
                    national_code=str(row[3].value),
                )
                try:
                    if exist_user:
                        if exist_user.credit.considered:
                            organization_user.total_considered_credit -= (
                                exist_user.credit.considered
                            )
                        organization_user.total_considered_credit += int(row[15].value)
                        db.add(organization_user)

                        # ? Append new User
                        exist_user.organization_id = organization_user.id
                        exist_user.credit.considered = int(row[15].value)
                    else:
                        # * Update Organization considered credit
                        organization_user.total_considered_credit += int(row[15].value)
                        db.add(organization_user)
                        # ? Generate new User -> validation = False
                        new_user = User(
                            organization_id=organization_user.id,
                            name=str(row[1].value),
                            last_name=str(row[2].value),
                            national_code=str(row[3].value),
                            phone_number=str(row[4].value),
                            father_name=str(row[5].value),
                            birth_place=str(row[6].value),
                            location_id=location,
                            postal_code=str(row[9].value),
                            tel=str(row[10].value),
                            address=str(row[11].value),
                            considered_credit=int(row[15].value),
                            personnel_number=str(row[12].value),
                            organizational_section=str(row[13].value),
                            job_class=str(row[14].value),
                        )

                        # ? Create Credit
                        credit = Credit(
                            user=new_user,
                            considered=int(row[15].value),
                        )

                        # ? Create Cash
                        cash = Cash(
                            user=new_user,
                        )

                        # ? Create Wallet
                        wallet_number = randint(100000, 999999)
                        wallet = Wallet(
                            user=new_user,
                            number=wallet_number,
                        )

                        db.add(new_user)
                        db.add(credit)
                        db.add(cash)
                        db.add(wallet)

                    await db.commit()
                    result_message.append(
                        "کاربر با کد ملی {} با موفقیت به سازمان شما پیوست".format(
                            str(row[3].value),
                        ),
                    )
                except:
                    text = "کاربر با شماره {} به دلیل نامشخص ثبت نشد! \n ".format(
                        row[0].value,
                        row[8].value,
                    )
                    error_message.append(text)

    print(error_message)
    print(result_message)
