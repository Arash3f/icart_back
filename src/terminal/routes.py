from random import randint

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src import deps
from src.schema import IDRequest
from src.terminal.crud import terminal as terminal_crud
from src.invoice.crud import invoice as invoice_crud
from src.terminal.schema import TerminalRead, TerminalCreate, TerminalVerifyOutput

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/terminal", tags=["terminal"])


# ---------------------------------------------------------------------------
@router.post("/create", response_model=TerminalRead)
async def create_terminal(
    *,
    create_data: TerminalCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> TerminalRead:
    """
    ! Generate new terminal

    Parameters
    ----------
    create_data
        New terminal
    db
        Target database connection

    Returns
    -------
    terminal
        New terminal

    Raises
    ------
    InvoiceNotFoundException
    """
    # * Verify duplicate number
    terminal_number = None
    stop = False
    while not stop:
        terminal_number = randint(1000000000, 9999999999)
        terminal_buf = await terminal_crud.find_by_number(
            db=db,
            terminal_number=terminal_number,
        )
        if not terminal_buf:
            stop = True
    # * Verify Invoice
    invoice = await invoice_crud.verify_existence_by_number(
        db=db,
        invoice_number=create_data.invoice_number,
    )
    # * Generate Terminal
    terminal = await terminal_crud.create(
        db=db,
        obj_in={
            "number": str(terminal_number),
            "invoice_id": invoice.id,
            "redirect_url": create_data.redirect_url,
        },
    )
    return terminal


# ---------------------------------------------------------------------------
@router.post("/verify", response_model=TerminalVerifyOutput)
async def verify_invoice(
    *,
    db: AsyncSession = Depends(deps.get_db),
    where_data: IDRequest,
) -> TerminalVerifyOutput:
    """
    ! Verify terminal

    Parameters
    ----------
    db
        Target database connection
    where_data
        filter data for find terminal

    Returns
    -------
    invoice
        Found invoice

    Raises
    ------
    TerminalNotFoundException
    """
    # * Verify merchant token
    terminal = await terminal_crud.verify_existence(db=db, terminal_id=where_data.id)
    return terminal
