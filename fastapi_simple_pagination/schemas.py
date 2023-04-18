from __future__ import annotations

from asyncio import Task, create_task, ensure_future
from typing import Any, Awaitable, Callable, Generic, List, Optional, Type, TypeVar

from pydantic import (
    AnyHttpUrl,
    Field,
    HttpUrl,
    NonNegativeInt,
    PositiveInt,
    parse_obj_as,
)
from pydantic.generics import GenericModel

from .common import Item, OtherItem


class Page(GenericModel, Generic[Item]):
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
    items: List[Item] = Field(
        default=...,
        description="The item list on this page.",
    )

    def map(
        self,
        mapper: Callable[[Item], OtherItem],
        type_: Optional[Type[OtherItem]] = None,
    ) -> "Page[OtherItem]":
        items = [mapper(item) for item in self.items]
        return self._build_new_page(items, type_)

    def _build_new_page(
        self, items: List[OtherItem], type_: Optional[Type[OtherItem]] = None
    ) -> "Page[OtherItem]":
        new_page = Page(  # type: ignore
            items=items,
            **dict(self),
        )
        if type_ is not None:
            return Page[type_].parse_obj(new_page)  # type: ignore
        return new_page

    async def map_async(
        self,
        mapper: Callable[[Item], Awaitable[OtherItem]],
        type_: Optional[Type[OtherItem]] = None,
    ) -> "Page[OtherItem]":
        item_tasks: List[Task[OtherItem]] = [
            create_task(mapper(item)) for item in self.items  # type: ignore
        ]
        return self._build_new_page([await task for task in item_tasks], type_)

    def validate_page(self, page_model: Type[_Page]) -> _Page:
        return parse_obj_as(page_model, self)


class CursorPage(GenericModel, Generic[Item]):
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
    current: HttpUrl = Field(
        description="The URL of the current page.",
    )
    next_url: Optional[HttpUrl] = Field(
        description="The next page URL.",
    )
    previous_url: Optional[HttpUrl] = Field(
        description="The previous page URL.",
    )
    items: List[Item] = Field(description="The items of the page.")

    def map(self, mapper: Callable[[Item], OtherItem]) -> "CursorPage[OtherItem]":
        items = [mapper(item) for item in self.items]
        return self._build_new_page(items)

    def _build_new_page(self, items: List[OtherItem]) -> "CursorPage[OtherItem]":
        new_page = CursorPage(  # type: ignore
            items=items,
            **self.dict(exclude={"items"}),
        )

        return new_page

    async def map_async(
        self, mapper: Callable[[Item], Awaitable[OtherItem]]
    ) -> "CursorPage[OtherItem]":
        item_tasks: List[Task[OtherItem]] = [
            ensure_future(mapper(item)) for item in self.items
        ]
        return self._build_new_page([await task for task in item_tasks])

    def validate_page(self, page_model: Type[_CursorPage]) -> _CursorPage:
        return parse_obj_as(page_model, self)


_CursorPage = TypeVar("_CursorPage", bound=CursorPage[Any])
_Page = TypeVar("_Page", bound=CursorPage[Any])
