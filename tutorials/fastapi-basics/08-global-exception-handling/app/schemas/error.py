from pydantic import BaseModel
from typing import Any, Optional

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Any] = None
