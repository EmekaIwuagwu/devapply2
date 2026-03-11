from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime


class AgentStatusResponse(BaseModel):
    is_running: bool
    current_strategy_id: Optional[uuid.UUID] = None
    last_run_time: Optional[datetime] = None
    last_run_status: Optional[str] = None


class AgentConfig(BaseModel):
    max_applications_per_run: int
    delay_between_submissions_sec: int
    stealth_mode: bool
    browser_type: str
    captcha_solving_enabled: bool


class AgentExecutionResponse(BaseModel):
    execution_id: uuid.UUID
    status: str
    start_time: datetime


class AgentLogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    execution_id: Optional[uuid.UUID] = None
