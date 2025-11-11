from pydantic import BaseModel
from typing import List, TypeVar, Generic

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """A generic model for paginated list responses."""
    object: str = "list"
    data: List[T]
    has_more: bool
    url: str