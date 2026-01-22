# from pydantic import BaseModel, Field
# from typing import List, Dict, Any, Optional
# from enum import Enum

# class AgentStatus(str, Enum):
#     PENDING = "pending"
#     RUNNING = "running"
#     COMPLETED = "completed"
#     FAILED = "failed"

# class AgentTask(BaseModel):
#     task_type: str = Field(..., description="research, summarize, analyze")
#     input_data: str
#     parameters: Optional[Dict[str, Any]] = {}

# class AgentRunRequest(BaseModel):
#     task: AgentTask
#     background: bool = False

# class AgentResponse(BaseModel):
#     task_id: str
#     status: AgentStatus
#     result: Optional[str] = None
#     error: Optional[str] = None

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentTask(BaseModel):
    task_type: str = Field(..., description="research, summarize, analyze")
    input_data: str
    parameters: Optional[Dict[str, Any]] = {}

class AgentRunRequest(BaseModel):
    task: AgentTask
    background: bool = False

class AgentResponse(BaseModel):
    task_id: str
    status: AgentStatus
    result: Optional[str] = None
    error: Optional[str] = None