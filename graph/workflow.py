from typing import Dict, List, Any, Tuple
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, Graph
from dataclasses import dataclass, field
from enum import Enum
import json

class WorkflowState(Enum):
    INIT = "init"
    VERIFY = "verify"
    PROCESS = "process"
    EXECUTE = "execute"
    FEEDBACK = "feedback"
    END = "end"

@dataclass
class CSRState:
    messages: List[BaseMessage] = field(default_factory=list)
    current_state: WorkflowState = WorkflowState.INIT
    verified: bool = False
    verification_attempts: int = 0
    user_context: Dict = field(default_factory=dict)
    confidence_score: float = 1.0
    requires_escalation: bool = False
    pending_action: Dict = field(default_factory=dict)
    feedback_submitted: bool = False
    processed: bool = False
    
class MetaCSRWorkflow:
    def __init__(self, tools, agent):
        self.tools = tools
        self.agent = agent
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        workflow = StateGraph(CSRState)
        
        # Add nodes
        workflow.add_node("verify_identity", self._verify_identity_node)
        workflow.add_node("process_query", self._process_query_node)
        workflow.add_node("execute_action", self._execute_action_node)
        workflow.add_node("collect_feedback", self._collect_feedback_node)
        workflow.add_node("end", self._end_node)
        
        # Add edges with conditions
        workflow.add_conditional_edges(
            "verify_identity",
            self._verify_condition,
            {
                True: "process_query",
                False: "verify_identity"
            }
        )
        
        # Updated mapping for process_query transitions
        workflow.add_conditional_edges(
            "process_query",
            self._route_state,
            {
                "execute": "execute_action",
                "feedback": "collect_feedback",
                "end": "end",
                
            }
        )
        
        workflow.add_edge("execute_action", "end")
        workflow.add_edge("collect_feedback", "end")
        
        # Set entry point
        workflow.set_entry_point("verify_identity")
        
        return workflow.compile()
    
    def _verify_identity_node(self, state: CSRState) -> CSRState:
        """Handle identity verification"""
        if not state.verified and state.verification_attempts < 3:
            # Extract credentials from last message if available
            last_message = state.messages[-1] if state.messages else None
            if isinstance(last_message, HumanMessage):
                # Simple credential extraction - enhance in production
                if "CUST" in last_message.content:
                    result = self.tools.verify_identity(
                        customer_id=last_message.content,
                        password="password123"  # In production, get from secure input
                    )
                    state.verified = result.success
                    if result.success:
                        state.user_context = result.data.get("user_info", {})
            
            state.verification_attempts += 1
            
        return state

    def _process_query_node(self, state: CSRState) -> CSRState:
        """Process user query and determine next action"""
        if state.processed:  # Prevent reprocessing
            return state
            
        if not state.messages:
            state.processed = True
            return state
        
        last_message = state.messages[-1]
        if not isinstance(last_message, (HumanMessage, dict)):
            state.processed = True
            return state
        
        # Get last message content
        message_content = last_message.content if isinstance(last_message, HumanMessage) else last_message.get("content", "")
        
        # Process message only if not already processed
        if not state.processed:
            try:
                # Get agent response
                response = self.agent.generate_response(
                    message=message_content,
                    chat_history=[msg for msg in state.messages if isinstance(msg, (dict, BaseMessage))],
                    user_context=state.user_context,
                    available_actions=[]  # Will be populated from tools if needed
                )
                
                # Update state based on response
                state.confidence_score = response.get("confidence", 1.0)
                state.requires_escalation = state.confidence_score < 0.7
                
                if response.get("suggested_actions"):
                    state.pending_action = response["suggested_actions"][0]
                
            except Exception as e:
                print(f"Error processing query: {str(e)}")
                state.requires_escalation = True
            
            state.processed = True
        
        return state
    
    def _execute_action_node(self, state: CSRState) -> CSRState:
        """Execute pending action if any"""
        if state.pending_action:
            try:
                result = self.tools.execute_action.run(
                    user_id=state.user_context.get("id"),
                    action_id=state.pending_action.get("id"),
                    params={}
                )
                state.pending_action = {}
            except Exception as e:
                print(f"Error executing action: {str(e)}")
                state.requires_escalation = True
        
        return state
    
    def _collect_feedback_node(self, state: CSRState) -> CSRState:
        """Collect feedback if needed"""
        if not state.feedback_submitted and state.requires_escalation:
            try:
                result = self.tools.log_feedback.run(
                    session_id="session_123",
                    rating=3,
                    comments="Escalated to human agent"
                )
                state.feedback_submitted = True
            except Exception as e:
                print(f"Error collecting feedback: {str(e)}")
        
        return state

    def _verify_condition(self, state: CSRState) -> bool:
        """Determine if verification should continue"""
        return state.verified or state.verification_attempts >= 3

    def _route_state(self, state: CSRState) -> str:
        """Determine next state based on current context"""
        if state.pending_action:
            return "execute"
        elif state.requires_escalation and not state.feedback_submitted:
            return "feedback"
        return "end"
    
    def invoke(self, state: CSRState) -> CSRState:
        """Execute the workflow"""
        # Reset processed flag for new invocation
        state.processed = False
        return self.graph.invoke(state)
    
    def _end_node(self, state: CSRState) -> CSRState:
        """Final state"""
        state.processed = False  # Reset for next message
        return state
