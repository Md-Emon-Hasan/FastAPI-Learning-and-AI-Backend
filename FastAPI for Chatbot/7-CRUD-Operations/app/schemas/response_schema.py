from pydantic import BaseModel
from pydantic import Field
from typing import Any
from typing import Optional

class APIResponse(BaseModel):
    status: str = Field(..., description="Status of the API response")
    data : Optional[Any] = None
    error : Optional[str] = None