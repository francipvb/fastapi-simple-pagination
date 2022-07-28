from asyncio import Task
from typing import Any, Awaitable, Callable, Generic, List, Optional, Type, TypeVar

from pydantic import AnyHttpUrl, Field, NonNegativeInt, PositiveInt
from pydantic.generics import GenericModel

from .common import _Item, _OtherItem


class Page(GenericModel, Generic[_Item]):
    count: int = Field(
        default=...,
        description="The total number of items in the database.",
    )
    previous: Optional[AnyHttpUrl] = Field(
        default=None,
        description="The URL to the previous page.",
    )
    next: Optional[AnyHttpUrl] = Field(
        default=None,
        description="The URL to the next page.",
    )
    first: AnyHttpUrl = Field(
        default=...,
        description="The URL to the first page.",
    )
    last: AnyHttpUrl = Field(
        default=...,
        description="The URL to the last page.",
    )
    current: AnyHttpUrl = Field(
        default=...,
        description="The URL to refresh the current page.",
    )

    page: int = Field(
        default=...,
        description="The current page number.",
    )
    items: List[_Item] = Field(
        default=...,
        description="The item list on this page.",
    )

    def map(self, mapper: Callable[[_Item], _OtherItem], type_: Type[_OtherItem]=Any) -> "Page[_OtherItem]":
        items = [mapper(item) for item in self.items]
        return self._build_new_page(items, type_)

    def _build_new_page(self, items: List[_OtherItem], type_: Type[_OtherItem]=Any) -> "Page[_OtherItem]":
        return Page[type_](
            items=items,
            **dict(self)
        )

    async def map_async(
        self, mapper: Callable[[_Item], Awaitable[_OtherItem]], type_: Type[_OtherItem]=Any
    ) -> "Page[_OtherItem]":
        item_tasks: List[Task[_OtherItem]] = [
            create_task(mapper(item)) for item in self.items  # type: ignore
        ]
        return self._build_new_page([await task for task in item_tasks], type_)

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

    def map(self, mapper: Callable[[_Item], _OtherItem], type_: Type[_OtherItem]=Any) -> "CursorPage[_OtherItem]":
        items = [mapper(item) for item in self.items]
        return self._build_new_page(items, type_)

    def _build_new_page(self, items: List[_OtherItem], type_: Type[_OtherItem]=Any) -> "CursorPage[_OtherItem]":
        return CursorPage[type_](
            items=items,
            **dict(self)
        )

    async def map_async(
        self, mapper: Callable[[_Item], Awaitable[_OtherItem]], type_: Type[_OtherItem]=Any
    ) -> "CursorPage[_OtherItem]":
        item_tasks: List[Task[_OtherItem]] = [
            create_task(mapper(item)) for item in self.items  # type: ignore
        ]
        return self._build_new_page([await task for task in item_tasks], type_)
