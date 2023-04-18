from typing import Any, List, Optional, Protocol, TypeVar

from pydantic import BaseModel, ConstrainedInt

Item = TypeVar("Item")
OtherItem = TypeVar("OtherItem", bound=BaseModel)


class QuerySize(ConstrainedInt):
    le = 100
    gt = 0


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
