"""empty message

Revision ID: db4c452c97e8
Revises: 6c500f562929
Create Date: 2023-11-15 15:46:41.549515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "db4c452c97e8"
down_revision: Union[str, None] = "6c500f562929"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cooperation_request",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tel", sa.String(), nullable=False),
        sa.Column("requester_name", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "AGENT",
                "ORGANIZATION",
                "MERCHANT",
                "SALES_AGENT",
                name="cooperationtype",
            ),
            nullable=True,
        ),
        sa.Column("status", sa.Boolean(), nullable=True),
        sa.Column(
            "field_of_work",
            sa.Enum(
                "HAIR_TRANSPLANT",
                "BEAUTY_CLINICS",
                "DENTAL_CLINICS",
                "FACIAL_GEL_BOTOX",
                "FURNITURE_STORES",
                "ELECTRICAL_APPLIANCES_STORE",
                "SLEEP_GOODS_STORES",
                "CARPET",
                "ELECTRICAL_APPLIANCES_REPAIRS",
                "LAPTOP",
                "MOBILE",
                "DIGITAL_ACCESSORIES",
                "TRAVEL_AGENCY",
                "RECREATIONAL_SPORTS_CENTERS",
                "LANGUAGE_TEACHING",
                "HAIRDRESSING_TRAINING",
                "STATIONERY",
                "WATCH_GALLERY",
                "GOLD_SALES",
                "JEWELRY_ACCESSORIES",
                "SUPER_MARKET",
                "FRUIT_SHOP",
                "DAIRY",
                "CAFE_RESTAURANT_FAST_FOOD",
                "CONFECTIONERY_DRIED_FRUIT",
                "ASIA_INSURANCE",
                "THIRD_PARTY_INSURANCE",
                "ADULT_CLOTHING",
                "CHILDREN_CLOTHING",
                "BAGS_AND_SHOES",
                "INTERIOR_DECORATION_DESIGNER",
                "BUILDING_EQUIPMENT",
                "MESON",
                "CAR_REPAIRS",
                "PHARMACY",
                "KITCHEN_ACCESSORIES_STORE",
                "EDUCATIONAL_SERVICES",
                "HOME_APPLIANCES",
                "AUDIO_AND_VIDEO_PRODUCT_STORE",
                "BAKERY",
                "GROCERY_STORES",
                "STATIONERY_STORES",
                "DTY_FRUITS_SHOP",
                "CLINICS",
                "CLOTHING_STORES",
                "HAIRDRESSERS",
                "LASER_CENTERS",
                "GOLD_AND_SILVER",
                "WATCH_SHOP",
                "PERFUME_AND_COLOGNE_STORE",
                "DECORATION",
                "COSMETIC",
                "PROTEIN_STORE",
                "CHANDELIERS_AND_ELECTRICAL_APPLIANCES",
                name="cooperationrequestfieldofworktype",
            ),
            nullable=True,
        ),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cooperation_request_id"),
        "cooperation_request",
        ["id"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_cooperation_request_id"), table_name="cooperation_request")
    op.drop_table("cooperation_request")
    # ### end Alembic commands ###
