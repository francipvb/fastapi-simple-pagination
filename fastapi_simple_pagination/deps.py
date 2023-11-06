import dataclasses
import math
import typing

import fastapi
from pydantic import AnyHttpUrl, BaseModel, PositiveInt, parse_obj_as

from fastapi_simple_pagination.common import QuerySize

from .schemas import Page

Item = typing.TypeVar("Item", bound=BaseModel)


@dataclasses.dataclass(frozen=True)
class PaginationRequestParams:
    request: fastapi.Request
    page: typing.Annotated[
        PositiveInt,
        fastapi.Query(
            description="The page number to get.",
        ),
    ] = 1
    size: QuerySize = 10

    def get_next(self, total_count: int):
        if self.page * self.size < total_count:
            url = self.request.url.replace_query_params(
                page=self.page + 1, size=self.size
            )

            return parse_obj_as(AnyHttpUrl, str(url))

        return None

    def get_previous(self, total_count: int):
        if self.page > 1:
            url = self.request.url.replace_query_params(
                page=self.page - 1, size=self.size
            )

            return parse_obj_as(AnyHttpUrl, str(url))

        return None

    def get_first(self):
        return parse_obj_as(
            AnyHttpUrl,
            str(self.request.url.replace_query_params(page=1, size=self.size)),
        )

    def get_last(self, total_count: int):
        last_page = math.ceil(total_count / self.size) or 1
        raw_url = str(
            self.request.url.replace_query_params(page=last_page, size=self.size)
        )

        return parse_obj_as(AnyHttpUrl, raw_url)

    def paginated(
        self, items: typing.List[Item], total_count: typing.Optional[int] = None
    ) -> Page[Item]:
        count = total_count or len(items)
        return Page(
            count=count,
            items=items[: self.size],
            page=self.page,
            next=self.get_next(count),
            previous=self.get_previous(count),
            first=self.get_first(),
            last=self.get_last(count),
            current=parse_obj_as(AnyHttpUrl, str(self.request.url)),
        )

    def get_offset(self):
        return (self.page - 1) * self.size
