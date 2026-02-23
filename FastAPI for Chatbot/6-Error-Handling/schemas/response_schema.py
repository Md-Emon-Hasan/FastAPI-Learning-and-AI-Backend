from pydantic import BaseModel
from typing import Optional
from typing import Any

class APIResponse(BaseModel):
    status : str
    data : Optional[Any] = None
    error : Optional[str] = None