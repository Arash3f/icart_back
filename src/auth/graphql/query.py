import strawberry
from strawberry.types import Info

from src.graphql.decorator import is_login_active


@is_login_active
def example(
    info: Info,
) -> str:
    return "Hello {}".format(info.user.first_name)


@strawberry.type
class Query:
    last_user: str = strawberry.field(resolver=example)
