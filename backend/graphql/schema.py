import strawberry
from backend.graphql.mutations.user_mutation import Mutation as UserMutation

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "GraphQL is working!"

schema = strawberry.Schema(query=Query, mutation=UserMutation)
