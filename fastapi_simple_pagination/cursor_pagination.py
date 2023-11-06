from dataclasses import dataclass
from typing import Annotated, Any, Callable, List

from fastapi import Query, Request
from pydantic import AnyHttpUrl, NonNegativeInt, parse_obj_as

from .common import CountItems, Item, OtherItem, PaginatedMethodProtocol, QuerySize
from .schemas import CursorPage


def _identity(item: Any) -> Any:
    return item


@dataclass()
class CursorPaginationParams:
    request: Request
    offset: Annotated[
        NonNegativeInt,
        Query(
            description="Where to start retrieving.",
        ),
    ] = 0
    size: QuerySize = 10

    async def paginated(
        self,
        items_getter: PaginatedMethodProtocol[Item],
        item_counter: CountItems,
        item_mapper: Callable[[Item], OtherItem] = _identity,
        **kwargs: Any,
    ) -> CursorPage[OtherItem]:
        item_list = await items_getter(size=self.size, offset=self.offset, **kwargs)
        item_count = await item_counter(**kwargs)
        has_next = self.offset + self.size < item_count
        items = [item_mapper(i) for i in item_list]

        return self._build_page(item_count, items, has_next)

    def _build_page(
        self, item_count: int, item_list: List[OtherItem], has_next: bool
    ) -> CursorPage[OtherItem]:
        return CursorPage(
            items=item_list,
            count=item_count,
            current=parse_obj_as(AnyHttpUrl, str(self.request.url)),
            next_url=self._build_next_url() if has_next else None,
            previous_url=self._build_previous_url() if self.offset > 0 else None,
            size=self.size,
            offset=self.offset,
        )

    def _build_next_url(self) -> AnyHttpUrl:
        new_url = self.request.url.remove_query_params(
            ["offset", "size"]
        ).include_query_params(
            offset=self.offset + self.size,
            size=self.size,
        )

        return parse_obj_as(AnyHttpUrl, str(new_url))

    def _build_previous_url(self) -> AnyHttpUrl:
        offset = self.offset - self.size
        if offset < 0:
            offset = 0
        new_url = self.request.url.remove_query_params(
            ["offset", "size"]
        ).include_query_params(offset=offset, size=self.size)
        return parse_obj_as(AnyHttpUrl, str(new_url))
