from typing import Dict, List, Optional, Any
from langchain_core.tools import tool
from datetime import datetime
import json
from dataclasses import dataclass
import requests
from enum import Enum

# ----------------------------
# Enumerations and Data Classes
# ----------------------------
class ActionPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ActionResult:
    success: bool
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None

# ----------------------------
# MetaCSRTools Class Definition
# ----------------------------
class MetaCSRTools:
    """Unified tools class for Meta CSR Agent"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _mock_api_call(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Mock API call for demonstration. Replace with real API calls in production.
        """
        # Identity verification
        if endpoint == "/auth/verify":
            return {
                "verified": data["customer_id"].startswith("USER"),
                "user_info": {
                    "id": data["customer_id"],
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }
        # Knowledge base search
        elif endpoint == "/kb/search":
            return {
                "articles": [
                    {
                        "title": "How to reset password",
                        "content": "Step by step guide...",
                        "relevance": 0.95
                    }
                ]
            }
        # Order status endpoint
        elif endpoint.startswith("/orders/") and endpoint.endswith("/status"):
            return {
                "order_number": endpoint.split("/")[2],
                "status": "shipped",
                "estimated_delivery": "2025-02-15",
                "tracking_number": "1234567890"
            }
        # User context endpoint
        elif endpoint.startswith("/users/") and endpoint.endswith("/context"):
            return {
                "subscription_status": "active",
                "last_login": "2025-02-13",
                "pending_actions": ["update_payment"],
                "available_actions": [
                    {
                        "id": "update_payment",
                        "title": "Update Payment Method",
                        "priority": ActionPriority.HIGH.value
                    }
                ]
            }
        # Update shipping address endpoint
        elif endpoint.startswith("/orders/") and endpoint.endswith("/update_shipping"):
            # For example, echo back the new address
            return {
                "order_number": endpoint.split("/")[2],
                "updated_address": data.get("new_address"),
                "status": "shipping address updated"
            }
        # Request refund endpoint
        elif endpoint.startswith("/orders/") and endpoint.endswith("/refund"):
            return {
                "order_number": endpoint.split("/")[2],
                "refund_status": "initiated",
                "refund_reason": data.get("reason", "Not specified")
            }
        # Email order details endpoint
        elif endpoint.startswith("/orders/") and endpoint.endswith("/email"):
            return {
                "order_number": endpoint.split("/")[2],
                "email_sent": True,
                "recipient": data.get("recipient")
            }
        # Update account details endpoint
        elif endpoint == "/account/update":
            return {
                "user_id": data.get("user_id"),
                "updated_fields": data.get("details"),
                "status": "account details updated"
            }
        # Schedule callback endpoint
        elif endpoint == "/crm/callback":
            return {
                "user_id": data.get("user_id"),
                "callback_time": data.get("callback_time"),
                "status": "callback scheduled"
            }
        
        return {"status": "success"}

    def verify_identity_impl(self, customer_id: str, password: str) -> ActionResult:
        try:
            response = self._mock_api_call("POST", "/auth/verify", {"customer_id": customer_id, "password": password})
            if response.get("verified", False):
                return ActionResult(
                    success=True,
                    message="Identity verified successfully",
                    data={"user_info": response.get("user_info", {})}
                )
            return ActionResult(
                success=False,
                message="Identity verification failed",
                error="Invalid credentials"
            )
        except Exception as e:
            return ActionResult(success=False, message="Verification error", error=str(e))

# ----------------------------
# Create a Global Instance of MetaCSRTools
# ----------------------------
meta_csr_tools = MetaCSRTools(api_base_url="https://api.example.com", api_key="your_api_key_here")

# ----------------------------
# Standalone Tool Functions
# ----------------------------

@tool
def verify_identity(customer_id: str, password: str) -> ActionResult:
    """
    Verify customer identity using their credentials.
    """
    return meta_csr_tools.verify_identity_impl(customer_id, password)

@tool
def query_knowledge_base(query: str, category: Optional[str] = None) -> ActionResult:
    """
    Search knowledge base for relevant information.
    """
    try:
        params = {"query": query}
        if category:
            params["category"] = category
        response = meta_csr_tools._mock_api_call("GET", "/kb/search", params)
        return ActionResult(
            success=True,
            message="Knowledge base query successful",
            data={"articles": response.get("articles", [])}
        )
    except Exception as e:
        return ActionResult(success=False, message="Knowledge base query failed", error=str(e))

@tool
def fetch_order_status(order_number: str) -> ActionResult:
    """
    Get current status of an order.
    """
    try:
        response = meta_csr_tools._mock_api_call("GET", f"/orders/{order_number}/status")
        return ActionResult(
            success=True,
            message="Order status retrieved successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to fetch order status", error=str(e))

@tool
def get_user_context(user_id: str) -> ActionResult:
    """
    Get complete user context including state and available actions.
    """
    try:
        response = meta_csr_tools._mock_api_call("GET", f"/users/{user_id}/context")
        return ActionResult(
            success=True,
            message="User context retrieved successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to fetch user context", error=str(e))

@tool
def execute_action(user_id: str, action_id: str, params: Optional[Dict] = None) -> ActionResult:
    """
    Execute an action on behalf of the user.
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", f"/actions/{action_id}/execute", {"user_id": user_id, "params": params or {}})
        return ActionResult(
            success=True,
            message=f"Action {action_id} executed successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message=f"Failed to execute action {action_id}", error=str(e))

@tool
def log_feedback(session_id: str, rating: int, comments: Optional[str] = None) -> ActionResult:
    """
    Log customer feedback for the session.
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", "/feedback/log", {"session_id": session_id, "rating": rating, "comments": comments})
        return ActionResult(
            success=True,
            message="Feedback logged successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to log feedback", error=str(e))

# ----------------------------
# Additional CRM Endpoints / Tools
# ----------------------------

@tool
def update_shipping_address(order_number: str, new_address: Dict[str, str]) -> ActionResult:
    """
    Update the shipping address for a specific order.
    
    Args:
        order_number: The order number to update.
        new_address: A dictionary with address details (e.g., street, city, state, zip).
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", f"/orders/{order_number}/update_shipping", {"new_address": new_address})
        return ActionResult(
            success=True,
            message="Shipping address updated successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to update shipping address", error=str(e))

@tool
def request_refund(order_number: str, reason: str) -> ActionResult:
    """
    Request a refund for a given order.
    
    Args:
        order_number: The order number.
        reason: Reason for the refund request.
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", f"/orders/{order_number}/refund", {"reason": reason})
        return ActionResult(
            success=True,
            message="Refund request initiated successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to initiate refund", error=str(e))

@tool
def send_order_email(recipient: str, order_number: str) -> ActionResult:
    """
    Email the order details to the specified recipient.
    
    Args:
        recipient: The email address to send the details.
        order_number: The order number.
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", f"/orders/{order_number}/email", {"recipient": recipient})
        return ActionResult(
            success=True,
            message="Order details emailed successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to email order details", error=str(e))

@tool
def update_account_details(user_id: str, details: Dict[str, Any]) -> ActionResult:
    """
    Update account or billing details for a user.
    
    Args:
        user_id: The user's ID.
        details: A dictionary containing the details to update.
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", "/account/update", {"user_id": user_id, "details": details})
        return ActionResult(
            success=True,
            message="Account details updated successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to update account details", error=str(e))

@tool
def schedule_callback(user_id: str, callback_time: str) -> ActionResult:
    """
    Schedule a callback for the user at a specified time.
    
    Args:
        user_id: The user's ID.
        callback_time: The desired callback time as a string.
    """
    try:
        response = meta_csr_tools._mock_api_call("POST", "/crm/callback", {"user_id": user_id, "callback_time": callback_time})
        return ActionResult(
            success=True,
            message="Callback scheduled successfully",
            data=response
        )
    except Exception as e:
        return ActionResult(success=False, message="Failed to schedule callback", error=str(e))
