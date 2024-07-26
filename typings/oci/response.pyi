from typing import Generic, Mapping, TypeVar

from oci.request import Request

_T = TypeVar("_T")
_U = TypeVar("_U")

class Response(Generic[_T, _U]):
    status: int
    headers: Mapping[str, str]
    request: Request[_U]
    next_page: str | None
    request_id: str | None
    has_next_page: bool
    data: _T
