from typing import Generic, List, Optional, TypeVar

import pydantic
from pydantic.generics import GenericModel

_IT = TypeVar("_IT", bound=pydantic.BaseModel)


class Page(GenericModel, Generic[_IT]):
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
    items: List[_IT] = pydantic.Field(
        default=...,
        description="The item list on this page.",
    )
