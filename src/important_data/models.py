from sqlalchemy import Column, Integer, Float, CheckConstraint

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class ImportantData(Base, BaseMixin):
    __tablename__ = "important_data"

    registration_fee = Column(Integer, nullable=False)
    blue_card_cost = Column(Integer, nullable=True)
    icart_members = Column(Integer, default=7)
    referral_user_number = Column(Integer, default=1)
    referral_transactions = Column(Integer, default=20)
    referral_transaction_percentage = Column(
        Float,
        CheckConstraint(
            "referral_transaction_percentage >= 0 AND referral_transaction_percentage <= 100",
        ),
        nullable=True,
    )
    referral_discount = Column(Integer, default=150000)
    referral_reward = Column(Integer, default=200000)
