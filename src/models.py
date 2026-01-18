
# src/models.py
from pydantic import BaseModel
from typing import Optional

class PipelineState(BaseModel):
    specification: str
    plan: Optional[str] = None
    stripped_plan: Optional[str] = None
    implementation_result: Optional[str] = None
    judge_verdict: Optional[str] = None
    final_output: Optional[str] = None
    error_occurred: bool = False
    error_message: Optional[str] = None