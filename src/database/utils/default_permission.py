from pydantic import BaseModel

from src.permission import permission_codes as permission


class DefaultRolePermission(BaseModel):
    name: str
    permissions: list[int]


default_role_permission: list[DefaultRolePermission] = [
    DefaultRolePermission(
        name="کاربر ساده",
        permissions=[
            permission.VIEW_ABILITY,
        ],
    ),
    DefaultRolePermission(
        name="نماینده",
        permissions=[
            permission.VIEW_MERCHANT,
        ],
    ),
    DefaultRolePermission(
        name="پذیرنده",
        permissions=[
            permission.VIEW_MERCHANT,
        ],
    ),
    DefaultRolePermission(
        name="کارشناس",
        permissions=[
            permission.VIEW_MERCHANT,
            permission.UPDATE_MERCHANT,
            permission.UPDATE_POSITION_REQUEST,
            permission.VIEW_POSITION_REQUEST,
            permission.VIEW_USER,
            permission.VIEW_USER_REQUEST,
            permission.UPDATE_AGENT,
            permission.UPDATE_ORGANIZATION,
            permission.CHANGE_USER_ACTIVITY,
        ],
    ),
    DefaultRolePermission(
        name="مرکز تماس",
        permissions=[
            permission.VIEW_TICKET,
            permission.RESPONSE_TICKET,
        ],
    ),
]
