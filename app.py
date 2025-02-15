import streamlit as st
import os
from typing import Dict, List
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from graph.workflow import MetaCSRWorkflow
from agents.csr_agent import MetaCSRAgent
from models.state import CSRState, WorkflowState

from dotenv import load_dotenv
load_dotenv()

from tools.tools import (
    verify_identity,
    query_knowledge_base,
    fetch_order_status,
    get_user_context,
    execute_action,
    log_feedback,
    update_shipping_address,
    request_refund,
    send_order_email,
    update_account_details,
    schedule_callback
)

# A simple wrapper to group standalone tool functions
class ToolsWrapper:
    def __init__(self):
        self.verify_identity = verify_identity
        self.query_knowledge_base = query_knowledge_base
        self.fetch_order_status = fetch_order_status
        self.get_user_context = get_user_context
        self.execute_action = execute_action
        self.log_feedback = log_feedback
        # Add new tools
        self.update_shipping_address = update_shipping_address
        self.request_refund = request_refund
        self.send_order_email = send_order_email
        self.update_account_details = update_account_details
        self.schedule_callback = schedule_callback

class MetaCSRApp:
    def __init__(self):
        self.tools = ToolsWrapper()
        self.agent = MetaCSRAgent(
            model_name="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1024
        )
        self.workflow = MetaCSRWorkflow(self.tools, self.agent)

    def initialize_session(self):
        """Initialize or reset session state"""
        if 'state_dict' not in st.session_state:
            st.session_state.state_dict = CSRState().to_dict()
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'user_context' not in st.session_state:
            st.session_state.user_context = {}
        if 'current_order' not in st.session_state:
            st.session_state.current_order = None

    def get_current_state(self) -> CSRState:
        """Retrieve the current state from session storage"""
        return CSRState.from_dict(st.session_state.state_dict)

    def update_state(self, state: CSRState):
        """Update session state dictionary"""
        st.session_state.state_dict = state.to_dict()

    def render_header(self):
        st.title("Customer Service Assistant")
        st.markdown("""
        Welcome to our customer service portal. How can we help you today?
        """)

    def render_sidebar(self):
        st.sidebar.header("Help Center")
        
        # Show verification status
        current_state = self.get_current_state()
        if current_state.verified:
            st.sidebar.success("✓ Verified User")
            if current_state.user_context:
                st.sidebar.subheader("User Information")
                st.sidebar.json(current_state.user_context)
        else:
            st.sidebar.warning("⚠ Not Verified")
            st.sidebar.info("Please verify your identity to continue")

        # Show available features
        st.sidebar.subheader("Available Services")
        st.sidebar.markdown("""
        - 📦 **Order Management**
          - Track order status
          - Update shipping address
          - Request refunds
          - Get order details via email
        
        - ❓ **General Support**
          - Product information
          - Shipping policies
          - Return policies
          - Technical support
        
        - 🔄 **Real-time Updates**
          - Order status notifications
          - Shipping updates
          - Delivery confirmations
        """)
        
        # Show current order if available
        if st.session_state.current_order:
            st.sidebar.subheader("Current Order")
            st.sidebar.json(st.session_state.current_order)
            
    def render_verification(self):
        st.header("Identity Verification")
        with st.form("verification_form"):
            customer_id = st.text_input("Customer ID")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Verify Identity")
            if submitted:
                result = self.tools.verify_identity.run(
                    {"customer_id": customer_id, "password": password},
                    callbacks=[]
                )
                current_state = self.get_current_state()
                if result.success:
                    current_state.verified = True
                    current_state.user_context = result.data.get("user_info", {})
                    self.update_state(current_state)
                    st.session_state.user_context = result.data.get("user_info", {})
                    st.success("Identity verified successfully!")
                    st.rerun()
                else:
                    current_state.verification_attempts += 1
                    self.update_state(current_state)
                    st.error(result.message)

    def render_action_buttons(self, actions: List[Dict]):
        if not actions or not isinstance(actions, list):
            return
        valid_actions = [
            action for action in actions 
            if isinstance(action, dict) and "id" in action and "title" in action
        ]
        if valid_actions:
            cols = st.columns(len(valid_actions))
            for idx, action in enumerate(valid_actions):
                with cols[idx]:
                    if st.button(action["title"], key=f"action_{action['id']}_{idx}"):
                        self.execute_action(action)

    def render_order_actions(self):
        if not st.session_state.current_order:
            return

        st.subheader("Order Actions")
        order_number = st.session_state.current_order.get("order_number")
        
        with st.expander("Update Shipping Address"):
            with st.form("shipping_form"):
                address = st.text_area("New Shipping Address")
                if st.form_submit_button("Update Address"):
                    result = self.tools.update_shipping_address.run(
                        order_number,
                        {"address": address}
                    )
                    if result.success:
                        st.success(result.message)
                    else:
                        st.error(result.message)

        with st.expander("Request Refund"):
            with st.form("refund_form"):
                reason = st.text_area("Refund Reason")
                if st.form_submit_button("Submit Refund Request"):
                    result = self.tools.request_refund.run(
                        order_number,
                        reason
                    )
                    if result.success:
                        st.success(result.message)
                    else:
                        st.error(result.message)

        with st.expander("Email Order Details"):
            with st.form("email_form"):
                email = st.text_input("Email Address")
                if st.form_submit_button("Send Order Details"):
                    result = self.tools.send_order_email.run(
                        email,
                        order_number
                    )
                    if result.success:
                        st.success(result.message)
                    else:
                        st.error(result.message)

    # def render_account_actions(self):
    #     if not st.session_state.user_context:
    #         return

    #     st.subheader("Account Actions")
        
    #     with st.expander("Update Account Details"):
    #         with st.form("account_form"):
    #             email = st.text_input("Email")
    #             phone = st.text_input("Phone")
    #             if st.form_submit_button("Update Details"):
    #                 result = self.tools.update_account_details.run(
    #                     st.session_state.user_context.get("id"),
    #                     {"email": email, "phone": phone}
    #                 )
    #                 if result.success:
    #                     st.success(result.message)
    #                 else:
    #                     st.error(result.message)

    #     with st.expander("Schedule Callback"):
    #         with st.form("callback_form"):
    #             callback_time = st.date_input("Callback Date")
    #             if st.form_submit_button("Schedule Callback"):
    #                 result = self.tools.schedule_callback.run(
    #                     st.session_state.user_context.get("id"),
    #                     callback_time.isoformat()
    #                 )
    #                 if result.success:
    #                     st.success(result.message)
    #                 else:
    #                     st.error(result.message)

    def render_chat_interface(self):
        st.header("Chat Support")
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "suggested_actions" in message and message["suggested_actions"]:
                    self.render_action_buttons(message["suggested_actions"])
        
        # Render order and account actions if user is verified
        current_state = self.get_current_state()
        if current_state.verified:
            self.render_order_actions()
            

        # Chat input box appears only if conversation is not terminal
        if current_state.current_state != WorkflowState.END:
            if user_input := st.chat_input("Type your message here..."):
                self.update_chat_history(user_input)
                st.rerun()
        else:
            st.info("Conversation ended. Please start a new conversation to continue.")

    def generate_agent_response(self, user_input: str) -> Dict:
        response = self.agent.generate_response(
            message=user_input,
            chat_history=st.session_state.messages,
            user_context=st.session_state.user_context,
            available_actions=self.get_available_actions()
        )
        return {
            "role": "assistant",
            "content": response.get("response", ""),
            "suggested_actions": response.get("suggested_actions", [])
        }

    def update_chat_history(self, user_input: str):
        # Append user message
        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)
        try:
            agent_response = self.generate_agent_response(user_input)
            st.session_state.messages.append(agent_response)
            # Update workflow state based on the conversation
            state = self.get_current_state()
            state.messages = st.session_state.messages
            new_state = self.workflow.invoke(state)
            self.update_state(new_state)
            if new_state.requires_escalation:
                st.session_state.messages.append({
                    "role": "system",
                    "content": "This conversation will be escalated to a human agent."
                })
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            st.error("An error occurred generating a response. Please try again.")

    def execute_action(self, action: Dict):
        if not action or "id" not in action:
            st.error("Invalid action")
            return
        result = self.tools.execute_action.run(
            {"user_id": st.session_state.user_context.get("id"), "action_id": action["id"]},
            callbacks=[]
        )
        if result.success:
            st.success(result.message)
            st.session_state.messages.append({
                "role": "system",
                "content": f"Action executed: {action.get('title', action['id'])}"
            })
            st.rerun()
        else:
            st.error(result.message or "Action execution failed")

    def get_available_actions(self) -> List[Dict]:
        if not st.session_state.state_dict.get("verified", False):
            return []
        result = self.tools.get_user_context.run(
            st.session_state.user_context.get("id", ""),
            callbacks=[]
        )
        return result.data.get("available_actions", []) if result.success else []

    def run(self):
        self.initialize_session()
        self.render_header()
        self.render_sidebar()
        current_state = self.get_current_state()
        if not current_state.verified:
            self.render_verification()
        else:
            if current_state.current_state == WorkflowState.END:
                st.info("Conversation ended.")
                if st.button("Start New Conversation"):
                    st.session_state.state_dict = CSRState().to_dict()
                    st.session_state.messages = []
                    st.rerun()
            else:
                self.render_chat_interface()
                
        if current_state.requires_escalation:
            if st.button("Connect to Human Agent"):
                result = self.tools.execute_action.run(
                    {"user_id": current_state.user_context.get("id"), "action_id": "escalate_to_human"},
                    callbacks=[]
                )
                st.info("Connecting to a human agent...")

if __name__ == "__main__":
    app = MetaCSRApp()
    app.run()