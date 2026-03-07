"""
Data schemas for JARVIS using Pydantic
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4


class Utterance(BaseModel):
    """Speech input or typed command"""
    utterance_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str  # "microphone", "keyboard", "vision", "mcu"
    raw_audio_ref: Optional[str] = None
    text: str
    language: str = "en"
    stt_confidence: float = 0.0
    tokens: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedCommand(BaseModel):
    """Parsed intent and entities from utterance"""
    command_id: str = Field(default_factory=lambda: str(uuid4()))
    utterance_id: str
    intent: str
    intent_confidence: float
    slots: Dict[str, Any] = Field(default_factory=dict)
    ambiguity: List[str] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    text: str = ""  # Original text for context


class Step(BaseModel):
    """Single execution step in a plan"""
    step_id: str
    tool: str
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    permission_level: str = "ask"  # "allow", "ask", "deny"
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)


class ActionPlan(BaseModel):
    """Complete execution plan with multiple steps"""
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    command_id: str
    steps: List[Step]
    priority: int = 50
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str


class TaskState(BaseModel):
    """Runtime state of executing task"""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    action_id: str
    current_step: Optional[str] = None
    pending_steps: List[str] = Field(default_factory=list)
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 0.0
    error: Optional[str] = None
    status: str = "pending"  # "pending", "running", "success", "failed"


class MemoryNode(BaseModel):
    """Vector store entry"""
    node_id: str = Field(default_factory=lambda: str(uuid4()))
    type: str  # "preference", "fact", "note", "file_reference"
    text: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    source: str  # "user_statement", "imported_file"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolManifest(BaseModel):
    """Tool capability registration"""
    tool_id: str
    name: str
    capabilities: List[str]
    permission_level_default: str = "ask"
    endpoint: str = "local"
    health: Dict[str, Any] = Field(default_factory=dict)


class AuditLogEntry(BaseModel):
    """Append-only audit log entry"""
    log_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    actor: str
    action: str
    target: str
    input_data: Dict[str, Any] = Field(default_factory=dict, alias="input")
    result: Dict[str, Any] = Field(default_factory=dict)
    signed_by: Optional[str] = None


class ExecutionResult(BaseModel):
    """Result of tool execution"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)
