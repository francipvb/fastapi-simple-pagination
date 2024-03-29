from __future__ import annotations

from asyncio import Task, create_task, ensure_future
from typing import Any, Awaitable, Callable, Generic, List, Optional, Type, TypeVar

import pydantic

_T = TypeVar("_T", bound=pydantic.BaseModel)
_TM = TypeVar("_TM", bound=pydantic.BaseModel)


class Page(pydantic.BaseModel, Generic[_T]):
    count: int = pydantic.Field(
        default=...,
        description="The total number of items in the database.",
    )
    previous: Optional[pydantic.AnyHttpUrl] = pydantic.Field(
        default=None,
        description="The URL to the previous page.",
    )
    next: Optional[pydantic.AnyHttpUrl] = pydantic.Field(
        default=None,
        description="The URL to the next page.",
    )
    first: pydantic.AnyHttpUrl = pydantic.Field(
        default=...,
        description="The URL to the first page.",
    )
    last: pydantic.AnyHttpUrl = pydantic.Field(
        default=...,
        description="The URL to the last page.",
    )
    current: pydantic.AnyHttpUrl = pydantic.Field(
        default=...,
        description="The URL to refresh the current page.",
    )

    page: int = pydantic.Field(
        default=...,
        description="The current page number.",
    )
    items: List[_T] = pydantic.Field(
        default=...,
        description="The item list on this page.",
    )

    def map(
        self,
        mapper: Callable[[_T], _TM],
        type_: Optional[Type[_TM]] = None,
    ) -> Page[_TM]:
        items = [mapper(item) for item in self.items]
        return self._build_new_page(items, type_)

    def _build_new_page(
        self, items: List[_TM], type_: Optional[Type[_TM]] = None
    ) -> Page[_TM]:
        new_page = Page(  # type: ignore
            items=items,
            **dict(self),
        )
        if type_ is not None:
            return Page[type_].parse_obj(new_page)  # type: ignore
        return new_page

    async def map_async(
        self,
        mapper: Callable[[_T], Awaitable[_TM]],
        type_: Optional[Type[_TM]] = None,
    ) -> Page[_TM]:
        item_tasks: List[Task[_TM]] = [
            create_task(mapper(item)) for item in self.items  # type: ignore
        ]
        return self._build_new_page([await task for task in item_tasks], type_)

    def validate_page(self, page_model: type[_Page]) -> _Page:
        return page_model.model_validate(self.model_dump())


class CursorPage(pydantic.BaseModel, Generic[_T]):
    """An offset and size paginated list."""

    offset: pydantic.NonNegativeInt = pydantic.Field(
        description="The offset where to start retrieving.",
    )
    size: pydantic.PositiveInt = pydantic.Field(
        description="The size of the page.",
    )
    count: pydantic.NonNegativeInt = pydantic.Field(
        description="How many items are saved in the store.",
    )
    current: pydantic.AnyHttpUrl = pydantic.Field(
        description="The URL of the current page.",
    )
    next_url: Optional[pydantic.AnyHttpUrl] = pydantic.Field(
        description="The next page URL.",
    )
    previous_url: Optional[pydantic.AnyHttpUrl] = pydantic.Field(
        description="The previous page URL.",
    )
    items: List[_T] = pydantic.Field(description="The items of the page.")

    def map(self, mapper: Callable[[_T], _TM]) -> CursorPage[_TM]:
        items = [mapper(item) for item in self.items]
        return self._build_new_page(items)

    def _build_new_page(self, items: List[_TM]) -> CursorPage[_TM]:
        new_page = CursorPage(  # type: ignore
            items=items,
            **self.dict(exclude={"items"}),
        )

        return new_page

    async def map_async(
        self, mapper: Callable[[_T], Awaitable[_TM]]
    ) -> CursorPage[_TM]:
        item_tasks: List[Task[_TM]] = [
            ensure_future(mapper(item)) for item in self.items
        ]
        return self._build_new_page([await task for task in item_tasks])

    def validate_page(self, page_model: Type[_CursorPage]) -> _CursorPage:
        return page_model.model_validate(self.model_dump())


_CursorPage = TypeVar("_CursorPage", bound=CursorPage[Any])
_Page = TypeVar("_Page", bound=CursorPage[Any])
