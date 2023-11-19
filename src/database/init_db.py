from random import randint

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import UserInDB
from src.card.models import Card
from src.cash.models import Cash
from src.core.config import settings
from src.core.security import hash_password
from src.credit.models import Credit
from src.database.utils.default_permission import default_role_permission
from src.database.utils.locations import location_in
from src.database.utils.permissions import permissions_in
from src.important_data.crud import important_data as important_data_crud
from src.important_data.schema import ImportantDataCreate
from src.location.crud import location as location_crud
from src.location.schema import LocationCreate
from src.permission.crud import permission as permission_crud
from src.role.crud import role as role_crud
from src.role.crud import role_permission as role_permission_crud
from src.role.schema import RoleCreate, RolePermissionCreate
from src.user.crud import user as user_crud
from src.wallet.models import Wallet

# ---------------------------------------------------------------------------
admin_role = RoleCreate(name="ادمین")

important_data_in = ImportantDataCreate(registration_fee=490000)

roles_in: list[RoleCreate] = [
    RoleCreate(name="ادمین"),
    RoleCreate(name="نماینده"),
    RoleCreate(name="پذیرنده"),
    RoleCreate(name="سازمان"),
    RoleCreate(name="کاربر ساده"),
]


# ---------------------------------------------------------------------------
async def init_db(db: AsyncSession) -> None:
    """
    * Initial default data in database

    Parameters
    ----------
    db
        Target database connection

    Returns
    -------
    response
        result of operation
    """
    # ! Generate all project roles
    for role in roles_in:
        # Check roles except admin exists or not
        role_exist = await role_crud.find_by_name(db=db, name=role.name)
        if not role_exist:
            await role_crud.create(db=db, obj_in=role)

    # ! Generate Admin user
    admin_user = await user_crud.find_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )
    role_admin = await role_crud.find_by_name(db=db, name=admin_role.name)
    if not admin_user:
        admin_in_db = UserInDB(
            username=settings.ADMIN_USERNAME,
            password=hash_password(settings.ADMIN_PASSWORD),
            national_code=settings.ADMIN_NATIONAL_CODE,
            role_id=role_admin.id,
        )
        created_user = await user_crud.create(db=db, obj_in=admin_in_db)

        # ? Create Credit
        credit = Credit(
            user=created_user,
        )

        # ? Create Cash
        cash = Cash(
            user=created_user,
        )

        # ? Create Wallet
        wallet_number = randint(100000, 999999)
        wallet = Wallet(
            user=created_user,
            number=wallet_number,
        )
        credit.user = created_user

        db.add(credit)
        db.add(cash)
        db.add(wallet)
        await db.commit()

    # ! Generate all project permissions
    for perm in permissions_in:
        # Check if permission exists or not
        permission_exist = await permission_crud.find_by_code(db=db, code=perm.code)
        if not permission_exist:
            # Create permission
            permission_created = await permission_crud.create(db=db, obj_in=perm)
            # Add permission for admin role
            role_permission_in = RolePermissionCreate(
                role_id=role_admin.id,
                permission_id=permission_created.id,
            )
            await role_permission_crud.create(db=db, obj_in=role_permission_in)

    # ? Add default role permissions
    for obj in default_role_permission:
        role_exist = await role_crud.verify_existence_by_name(db=db, name=obj.name)
        for perm_code in obj.permissions:
            permission = await permission_crud.find_by_code(
                db=db,
                code=perm_code,
            )
            role_permission_in = RolePermissionCreate(
                role_id=role_exist.id,
                permission_id=permission.id,
            )
            await role_permission_crud.create(db=db, obj_in=role_permission_in)
    # ! Generate all project locations
    for location in location_in:
        # Check if location exists or not
        location_exist = await location_crud.find_by_name(db=db, name=location.name)
        if not location_exist:
            parent_id = None
            if location.parent_name:
                parent_location_exist = await location_crud.find_by_name(
                    db=db,
                    name=location.parent_name,
                )
                if not parent_location_exist:
                    parent_created = await location_crud.create(
                        db=db,
                        obj_in={"name": location.parent_name},
                    )
                    parent_id = parent_created.id
                else:
                    parent_id = parent_location_exist.id
            create_location_data: LocationCreate = LocationCreate(
                name=location.name,
                parent_id=parent_id,
            )
            await location_crud.create(db=db, obj_in=create_location_data)

    # ! Generate Important data
    find_important_data = await important_data_crud.get_important_data_count(db=db)
    if not find_important_data:
        await important_data_crud.create(db=db, obj_in=important_data_in)
