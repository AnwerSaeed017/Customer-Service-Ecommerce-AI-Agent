# state.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class WorkflowState(Enum):
    INIT = "init"
    VERIFY = "verify"
    PROCESS = "process"
    EXECUTE = "execute"
    FEEDBACK = "feedback"
    END = "end"

@dataclass
class CSRState:
    # Basic state attributes
    verified: bool = False
    verification_attempts: int = 0
    current_state: WorkflowState = WorkflowState.INIT
    
    # Context and messages
    messages: List[Dict] = field(default_factory=list)
    user_context: Dict = field(default_factory=dict)
    
    # Processing flags
    confidence_score: float = 1.0
    requires_escalation: bool = False
    processed: bool = False
    
    # Action and feedback tracking
    pending_action: Dict = field(default_factory=dict)
    feedback_submitted: bool = False

    def to_dict(self) -> Dict:
        """Convert state to dictionary for storage"""
        return {
            "verified": self.verified,
            "verification_attempts": self.verification_attempts,
            "current_state": self.current_state.value,
            "messages": self.messages,
            "user_context": self.user_context,
            "confidence_score": self.confidence_score,
            "requires_escalation": self.requires_escalation,
            "processed": self.processed,
            "pending_action": self.pending_action,
            "feedback_submitted": self.feedback_submitted
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CSRState':
        """Create state from dictionary"""
        state = cls()
        if data:
            state.verified = data.get("verified", False)
            state.verification_attempts = data.get("verification_attempts", 0)
            state.current_state = WorkflowState(data.get("current_state", WorkflowState.INIT.value))
            state.messages = data.get("messages", [])
            state.user_context = data.get("user_context", {})
            state.confidence_score = data.get("confidence_score", 1.0)
            state.requires_escalation = data.get("requires_escalation", False)
            state.processed = data.get("processed", False)
            state.pending_action = data.get("pending_action", {})
            state.feedback_submitted = data.get("feedback_submitted", False)
        return state