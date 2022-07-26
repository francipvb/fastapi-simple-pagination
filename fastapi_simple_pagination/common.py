from typing import Any, List, Optional, Protocol, TypeVar

from pydantic import BaseModel, ConstrainedInt

_Item = TypeVar("_Item", bound=BaseModel)


class QuerySize(ConstrainedInt):
    le = 100
    gt = 0


class PaginatedMethodProtocol(Protocol[_Item]):
    async def __call__(
        self,
        *args: Any,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs: Any,
    ) -> List[_Item]:
        ...


class CountItems(Protocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> int:
        ...
