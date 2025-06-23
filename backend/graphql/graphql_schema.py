import strawberry
from typing import List

@strawberry.type
class Topic:
    id: int
    title: str
    user_id: int

@strawberry.type
class Query:
    @strawberry.field
    def topics(self) -> List[Topic]:
        return [] 

schema = strawberry.Schema(query=Query)
