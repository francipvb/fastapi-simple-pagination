from typing import Annotated, Any, List, Optional, Protocol, TypeVar

from fastapi import Query
from pydantic import BaseModel, PositiveInt

Item = TypeVar("Item")
OtherItem = TypeVar("OtherItem", bound=BaseModel)


QuerySize = Annotated[
    PositiveInt,
    Query(description="The size of the page to be retrieve."),
]


class PaginatedMethodProtocol(Protocol[Item]):
    async def __call__(
        self,
        *,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Item]:
        ...


class CountItems(Protocol):
    async def __call__(self, **kwargs: Any) -> int:
        ...
