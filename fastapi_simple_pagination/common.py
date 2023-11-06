from typing import Annotated, Any, List, Optional, Protocol, TypeVar

from pydantic import BaseModel, Field

Item = TypeVar("Item")
OtherItem = TypeVar("OtherItem", bound=BaseModel)


QuerySize = Annotated[int, Field(gt=0, le=100)]


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
