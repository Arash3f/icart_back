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
]
