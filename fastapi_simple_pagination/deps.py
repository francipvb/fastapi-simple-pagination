import dataclasses
import math
import typing

import fastapi
import pydantic

from .schemas import Page

_T = typing.TypeVar("_T", bound=pydantic.BaseModel)


@dataclasses.dataclass(frozen=True)
class PaginationRequestParams(typing.Generic[_T]):
    request: fastapi.Request
    page: int = fastapi.Query(1, description="The page number to query.")
    size: int = fastapi.Query(10, description="The page size.")

    def get_next(self, total_count: int) -> typing.Optional[str]:
        if self.page * self.size < total_count:
            url = self.request.url.replace_query_params(
                page=self.page + 1, size=self.size
            )

            return str(url)

        return None

    def get_previous(self, total_count: int) -> typing.Optional[str]:
        if self.page > 1:
            url = self.request.url.replace_query_params(
                page=self.page - 1, size=self.size
            )

            return str(url)

        return None

    def get_first(self):
        return str(self.request.url.replace_query_params(page=1, size=self.size))

    def get_last(self, total_count: int):
        last_page = math.ceil(total_count / self.size) or 1
        return str(
            self.request.url.replace_query_params(page=last_page, size=self.size)
        )

    def paginated(
        self, items: typing.List[_T], total_count: typing.Optional[int] = None
    ) -> Page[_T]:
        count = total_count or len(items)
        return Page(
            count=count,
            items=items[: self.size],
            page=self.page,
            next=self.get_next(count),
            previous=self.get_previous(count),
            first=self.get_first(),
            last=self.get_last(count),
            current=str(self.request.url),
        )

    def get_offset(self):
        return (self.page - 1) * self.size
