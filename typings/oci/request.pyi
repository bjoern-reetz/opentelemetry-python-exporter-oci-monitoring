from typing import Generic, Mapping, TypeVar

_T = TypeVar("_T")

class Request(Generic[_T]):
    method: str
    url: str
    query_params: Mapping[str, str] | None
    header_params: Mapping[str, str]
    body: _T
    response_type: str
    enforce_content_headers: bool
