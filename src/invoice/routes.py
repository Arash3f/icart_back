from random import randint

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.installments.schema import InstallmentsCreate
from src.invoice.crud import invoice as invoice_crud
from src.invoice.schema import InvoiceCreate, InvoiceRead, InvoiceVerifyInput
from src.merchant.crud import merchant as merchant_crud
from src.installments.crud import installments as installments_crud

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/invoice", tags=["invoice"])


# ---------------------------------------------------------------------------
@router.post("/verify", response_model=InvoiceRead)
async def verify_invoice(
    *,
    db: AsyncSession = Depends(deps.get_db),
    filter_data: InvoiceVerifyInput,
) -> InvoiceRead:
    """
    ! Verify invoices in merchant site
    # Todo:
        Verify IP

    Parameters
    ----------
    db
        Target database connection
    filter_data
        filter data for find invoice

    Returns
    -------
    invoice
        Found invoice

    Raises
    ------
    InvoiceNotFoundException
    MerchantNotFoundException
    """
    # ? Verify merchant token
    merchant = await merchant_crud.verify_existence_by_number(
        db=db,
        number=filter_data.merchant_number,
    )
    invoice = await invoice_crud.verify_existence_by_number_and_merchant_user_id(
        db=db,
        user_id=merchant.user_id,
        invoice_number=filter_data.number,
    )

    return invoice


# # ---------------------------------------------------------------------------
# @router.post("/create", response_model=InvoiceRead)
# async def create_invoice(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     create_data: InvoiceCreate,
# ) -> InvoiceRead:
#     """
#     ! Create Invoice
#     # Todo:
#         Verify IP
#
#     Parameters
#     ----------
#     db
#         Target database connection
#     create_data
#         Necessary data for create
#
#     Returns
#     -------
#     invoice
#         New Invoice
#
#     Raises
#     ------
#     InvoiceNotFoundException
#     MerchantNotFoundException
#     """
#     parent_invoice = None
#
#     # * Verify merchant token
#     merchant = await merchant_crud.verify_existence_by_number(
#         db=db,
#         number=create_data.merchant_number,
#     )
#
#     # * Verify parent invoice
#     if create_data.parent_number:
#         parent_invoice = (
#             await invoice_crud.verify_existence_by_number_and_merchant_user_id(
#                 db=db,
#                 invoice_number=create_data.parent_number,
#                 user_id=merchant.user_id,
#             )
#         )
#
#     icart_number = randint(1000, 9999)
#
#     # todo: Create Installments
#     obj_in = InstallmentsCreate(
#
#     )
#     installments = await installments_crud.create(db=db, obj_in=)
#
#     invoice = await invoice_crud.create(
#         db=db,
#         obj_in={
#             "number": create_data.number,
#             "icart_number": icart_number,
#             "value": create_data.value,
#             "type": create_data.type,
#             "installments_id": installments.id,
#             "parent_id": parent_invoice,
#         },
#     )
#     return invoice
