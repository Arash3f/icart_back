import strawberry

from strawberry.fastapi import GraphQLRouter
from src.auth.graphql.query import Query as auth_query


# ! All Modeling Schema
auth_schema = strawberry.Schema(
    query=auth_query,
    # mutation=auth_mutation
)

# ! All Modeling Schema
graphql_app = GraphQLRouter(
    auth_schema,
)
