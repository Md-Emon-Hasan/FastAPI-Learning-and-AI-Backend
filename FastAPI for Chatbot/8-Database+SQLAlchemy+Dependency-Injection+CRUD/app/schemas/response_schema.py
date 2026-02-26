from pydantic import BaseModel
from typing import Any
from typing import Optional

class APIResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None