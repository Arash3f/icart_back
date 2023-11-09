from pydantic import BaseModel
from src.permission import permission_codes as permission

from src.ability.schema import AbilityCreate


class LinkedAbility(BaseModel):
    ability_name: str
    permission_code: int


# ! Prepare default abilities
VIEW_TICKET = "دیدن تیکت ها"
default_abilities: list[AbilityCreate] = [
    AbilityCreate(
        name=VIEW_TICKET,
    ),
]

# ! Prepare linked abilities
linked_abilities: list[LinkedAbility] = [
    LinkedAbility(
        ability_name=VIEW_TICKET,
        permission_code=permission.VIEW_TICKET,
    ),
]
