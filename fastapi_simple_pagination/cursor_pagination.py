from asyncio import create_task
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Optional

from fastapi import Query, Request
from pydantic import (
    AnyHttpUrl,
    Field,
    NonNegativeInt,
    PositiveInt,
    parse_obj_as,
)
from pydantic.generics import GenericModel

from .common import CountItems, PaginatedMethodProtocol, QuerySize, _Item


class CursorPage(GenericModel, Generic[_Item]):
    """An offset and size paginated list."""

    offset: NonNegativeInt = Field(
        description="The offset where to start retrieving.",
    )
    size: PositiveInt = Field(
        description="The size of the page.",
    )
    count: NonNegativeInt = Field(
        description="How many items are saved in the store.",
    )
    current: AnyHttpUrl = Field(
        description="The URL of the current page.",
    )
    next_url: Optional[AnyHttpUrl  ]= Field(
        description="The next page URL.",
    )
    previous_url: Optional[AnyHttpUrl  ]= Field(
        description="The previous page URL.",
    )
    items: List[_Item] = Field(description="The items of the page.")


@dataclass()
class CursorPaginationParams:
    request: Request
    offset: NonNegativeInt = Query(
        default=0,
        description="Where to start retrieving.",
    )
    size: QuerySize = Query(
        default=10,
        description="Size of the page.",
    )

    async def paginated(
        self,
        items_getter: PaginatedMethodProtocol[_Item],
        item_counter: CountItems,
        item_mapper: Optional[Callable[[_Item], _Item]]  = None,
        *args: Any,
        **kwargs: Any,
    ) -> CursorPage[_Item]:
        item_list = create_task(
            items_getter(*args, size=self.size, offset=self.offset, **kwargs)
        )
        item_count = create_task(item_counter(*args, **kwargs))
        has_next = create_task(
            items_getter(*args, offset=self.offset + self.size, size=1, **kwargs)
        )
        if item_mapper is not None:
            items = [item_mapper(i) for i in await item_list]
        else:
            items = await item_list

        return self._build_page(await item_count, items, len(await has_next) > 0)

    def _build_page(
        self, item_count: int, item_list: List[_Item], has_next: bool
    ) -> CursorPage[_Item]:
        return CursorPage(
            items=item_list,
            count=item_count,
            current=parse_obj_as(AnyHttpUrl, str(self.request.url)),
            next_url=self._build_next_url(item_list) if has_next else None,
            previous_url=self._build_previous_url() if self.offset > 0 else None,
            size=self.size,
            offset=self.offset,
        )

    def _build_next_url(self, items: List[_Item]):
        new_url = self.request.url.replace_query_params(
            offset=self.offset + len(items),
            size=self.size,
        )

        return parse_obj_as(AnyHttpUrl, str(new_url))

    def _build_previous_url(self):
        offset = self.offset - self.size
        if offset < 0:
            offset = 0
        new_url = self.request.url.replace_query_params(offset=offset, size=self.size)
        return parse_obj_as(AnyHttpUrl, str(new_url))
