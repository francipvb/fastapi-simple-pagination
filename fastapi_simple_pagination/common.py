from typing import Annotated, List, Optional, ParamSpec, Protocol, TypeVar

from fastapi import Query
from pydantic import BaseModel, PositiveInt

Item = TypeVar("Item")
OtherItem = TypeVar("OtherItem", bound=BaseModel)


QuerySize = Annotated[
    PositiveInt,
    Query(description="The size of the page to be retrieve."),
]

_P = ParamSpec("_P")


class PaginatedMethodProtocol(Protocol[Item, _P]):
    async def __call__(
        self,
        *args: _P.args,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs: _P.kwargs,
    ) -> List[Item]:
        ...


class CountItemsProtocol(Protocol[_P]):
    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> int:
        ...
