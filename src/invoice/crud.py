from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.invoice.exception import (
    InvoiceCannotDeletedException,
    InvoiceNotFoundException,
)
from src.invoice.models import Invoice
from src.invoice.schema import InvoiceCreate


# ---------------------------------------------------------------------------
class InvoiceCRUD(BaseCRUD[Invoice, InvoiceCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        invoice_id: UUID,
    ) -> Type[Invoice]:
        """
        ! Verify Invoice Existence

        Parameters
        ----------
        db
            Target database connection
        invoice_id
            Target Invoice ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        InvoiceNotFoundException
        """
        obj = await db.get(entity=self.model, ident=invoice_id)
        if not obj:
            raise InvoiceNotFoundException()

        return obj

    async def verify_existence_by_id_and_merchant_user_id(
        self,
        *,
        db: AsyncSession,
        invoice_id: UUID,
        user_id: UUID,
    ) -> Invoice:
        """
        ! Verify Invoice Existence By invoice's number and merchant userID

        Parameters
        ----------
        db
            Target database connection
        invoice_id
            Target Invoice ID
        user_id
            Target Merchant User ID

        Returns
        -------
        invoice_obj
            Found Item
        """
        q1 = self.model.merchant.user_id == user_id
        q2 = self.model.id == invoice_id
        response = await db.execute(select(self.model).where(and_(q1, q2)))

        invoice_obj = response.scalar_one_or_none()
        if invoice_obj:
            raise InvoiceNotFoundException()

        return invoice_obj

    async def verify_can_change(self, *, invoice_obj: Invoice) -> bool:
        """
        ! Verify Can Change Invoice

        Parameters
        ----------
        invoice_obj
            Target Invoice

        Returns
        -------
        response
            Result of operation

        Raises
        ------
        InvoiceCannotDeletedException
        """
        # ? Do not have child or parent or transaction id
        verify_parent = invoice_obj.parent_id
        verify_child = invoice_obj.child
        verify_transaction = invoice_obj.transaction
        if verify_parent or verify_child or verify_transaction:
            raise InvoiceCannotDeletedException()

        return True

    async def verify_existence_by_number_and_merchant_user_id(
        self,
        *,
        db: AsyncSession,
        invoice_number: UUID,
        user_id: UUID,
    ) -> Invoice:
        """
        ! Verify Invoice Existence By invoice's number and merchant userID

        Parameters
        ----------
        db
            Target database connection
        invoice_number
            Target Invoice Number
        user_id
            Target Merchant User ID

        Returns
        -------
        invoice_obj
            Found Item

        Raises
        ------
        InvoiceNotFoundException
        """
        q1 = Invoice.installments.merchant.user_id == user_id
        q2 = Invoice.number == invoice_number
        response = await db.execute(select(Invoice).where(and_(q1, q2)))

        invoice_obj = response.scalar_one_or_none()
        if invoice_obj:
            raise InvoiceNotFoundException()

        return invoice_obj

    async def verify_existence_by_number(
        self,
        *,
        db: AsyncSession,
        invoice_number: UUID,
    ) -> Invoice:
        """
        ! Verify Invoice Existence By invoice's number

        Parameters
        ----------
        db
            Target database connection
        invoice_number
            Target Invoice Number

        Returns
        -------
        invoice_obj
            Found Item

        Raises
        ------
        InvoiceNotFoundException
        """
        q2 = self.model.icart_number == invoice_number
        response = await db.execute(select(self.model).where(q2))

        invoice_obj = response.scalar_one_or_none()
        if not invoice_obj:
            raise InvoiceNotFoundException()

        return invoice_obj


# ---------------------------------------------------------------------------
invoice = InvoiceCRUD(Invoice)
