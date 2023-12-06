from sqlalchemy import or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from src import deps
from src.auth.exception import AccessDeniedException
from src.band_card.models import BankCard
from src.permission import permission_codes
from src.schema import IDRequest, ResultResponse, VerifyUserDep
from src.user.models import User
from src.band_card.exception import BankCardDuplicate, InValidBankCard
from src.band_card.crud import bank_card as bank_card_crud
from src.band_card.schemas import (
    BankCardRead,
    BankCardCreate,
    BankCardFilter,
    BankCardBase,
)
from src.utils.auth import verify_bank_card

# -------------------------------------------------------------
router = APIRouter(prefix="/bank_card", tags=["bank_card"])


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[BankCardRead])
async def read_bank_card_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission_codes.BANK_CARD_VIEW]),
    ),
    filter_data: BankCardFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[BankCardRead]:
    """
    ! Read Withdraw list

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    bank_card_list
        List of BankCard
    """
    # * Prepare filter fields
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.last_name = (
        or_(
            User.last_name.contains(filter_data.last_name),
        )
        if filter_data.last_name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.shaba_number = (
        (BankCard.shaba_number.contains(filter_data.shaba_number))
        if filter_data.shaba_number is not None
        else True
    )
    filter_data.card_number = (
        (BankCard.card_number.contains(filter_data.card_number))
        if filter_data.card_number is not None
        else True
    )

    # * Add filter fields
    query = (
        select(BankCard)
        .filter(
            and_(
                filter_data.name,
                filter_data.last_name,
                filter_data.national_code,
                filter_data.card_number,
                filter_data.shaba_number,
            ),
        )
        .order_by(BankCard.created_at.desc())
    ).join(BankCard.user)

    # * Have permissions
    if verify_data.is_valid:
        bank_card_list = await bank_card_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )
    # * Verify transaction receiver & transferor
    else:
        query = query.where(
            BankCard.user_id == verify_data.user.id,
        )
        bank_card_list = await bank_card_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )

    return bank_card_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=BankCardRead)
async def find_transaction_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission_codes.BANK_CARD_VIEW]),
    ),
    input_data: IDRequest,
) -> BankCardRead:
    """
    ! Find BankCard by id

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    input_data
        Target BankCard ID

    Returns
    -------
    withdraw
        Found Item

    Raises
    ------
    BankCardNotFound
    AccessDeniedException
    """
    # ? Verify transaction existence
    bank_card = await bank_card_crud.verify_existence(
        db=db,
        bank_card_id=input_data.id,
    )

    # * Have permissions
    if verify_data.is_valid:
        return bank_card
    # * Verify transaction receiver & transferor
    else:
        if bank_card.user_id == verify_data.user.id:
            return bank_card
        else:
            raise AccessDeniedException()


# -------------------------------------------------------------
@router.post("/create", response_model=BankCardRead)
async def create_bank_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_v3(),
    ),
    bank_card_in: BankCardBase,
):
    card_exist = await bank_card_crud.find_by_bank_card_number(
        db=db,
        card_number=bank_card_in.card_number,
    )
    if card_exist:
        raise BankCardDuplicate()
    verify = verify_bank_card(
        user=current_user,
        card_number=bank_card_in.card_number,
        shaba_number=bank_card_in.shaba_number,
    )
    if not verify:
        raise InValidBankCard()

    create_data = BankCardCreate(
        **bank_card_in.model_dump(),
        user_id=current_user.id,
    )
    bank_card_created = await bank_card_crud.create(db=db, obj_in=create_data)

    return bank_card_created


# -------------------------------------------------------------
@router.delete("/delete", response_model=ResultResponse)
async def delete_bank_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    where: IDRequest,
) -> ResultResponse:
    bank_card = await bank_card_crud.verify_existence_by_id_and_user_id(
        db=db,
        user_id=current_user.id,
        bank_card_id=where.id,
    )
    bank_card_crud.delete(db=db, item_id=bank_card.id)

    return ResultResponse(result="Card Deleted Successfully")
