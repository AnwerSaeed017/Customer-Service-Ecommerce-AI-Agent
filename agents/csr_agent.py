from typing import Dict, List, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json

class MetaCSRAgent:
    """CSR Agent implementation for handling customer interactions"""
    
    def __init__(self, model_name: str, temperature: float, max_tokens: int):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.prompt = self._create_prompt()

    def _create_prompt(self) -> ChatPromptTemplate:
        system_prompt = """You are an advanced customer service representative with access to various tools and APIs. Your role is to:

1. Help customers with their inquiries and issues
2. Use available tools to verify identity and fetch information
3. Suggest relevant actions based on customer context
4. Guide customers through processes step by step
5. Collect feedback when appropriate

Available tools and their purposes:
- verify_identity: Check customer credentials
- query_knowledge_base: Find relevant information
- fetch_order_status: Check order status
- execute_action: Perform actions on behalf of the customer
- log_feedback: Record customer satisfaction

Guidelines:
- Always verify identity before providing sensitive information
- Maintain a professional and friendly tone
- Escalate to human support if confidence is low
- Suggest relevant next actions based on context
- Confirm before executing important actions
- Explain processes clearly
- Handle errors gracefully

Current user context: {user_context}
Previous interactions: {chat_history}
Available actions: {available_actions}
"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

    def analyze_sentiment(self, message: str) -> float:
        """Analyze customer message sentiment to adjust response tone"""
        # In production, use a proper sentiment analysis model
        positive_words = ['happy', 'great', 'thanks', 'good', 'excellent']
        negative_words = ['angry', 'bad', 'terrible', 'upset', 'frustrated']
        
        words = message.lower().split()
        sentiment = sum(word in positive_words for word in words) - sum(word in negative_words for word in words)
        return max(min((sentiment + 1) / 2, 1), 0)  # Normalize to 0-1

    def determine_intent(self, message: str) -> Dict[str, Any]:
        """Determine customer intent from message"""
        # In production, use a proper intent classification model
        intents = {
            'order_status': ['order', 'tracking', 'shipment', 'delivery'],
            'technical_support': ['error', 'problem', 'not working', 'broken'],
            'account_help': ['password', 'login', 'account', 'profile'],
            'billing': ['payment', 'charge', 'bill', 'invoice']
        }
        
        message_lower = message.lower()
        detected_intents = {}
        
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents[intent] = True
        
        return detected_intents or {'general_inquiry': True}

    def generate_response(self, 
                         message: str, 
                         chat_history: List[Dict], 
                         user_context: Dict,
                         available_actions: List[Dict]) -> Dict[str, Any]:
        """Generate appropriate response based on context and message"""
        
        # Analyze message
        sentiment = self.analyze_sentiment(message)
        intents = self.determine_intent(message)
        
        # Prepare context for prompt
        context = {
            "chat_history": chat_history,
            "input": message,
            "user_context": json.dumps(user_context, indent=2),
            "available_actions": json.dumps(available_actions, indent=2)
        }
        
        # Get response from LLM
        response = self.prompt | self.llm
        result = response.invoke(context)
        
        return {
            "response": result.content,
            "sentiment": sentiment,
            "intents": intents,
            "confidence": 0.85,  # In production, use actual confidence score
            "suggested_actions": self._suggest_actions(intents, user_context, available_actions)
        }

    def _suggest_actions(self, 
                        intents: Dict[str, bool], 
                        user_context: Dict,
                        available_actions: List[Dict]) -> List[Dict]:
        """Suggest relevant actions based on intent and context"""
        suggestions = []
        
        for action in available_actions:
            # Match actions to intents
            if 'order_status' in intents and action['id'].startswith('order_'):
                suggestions.append(action)
            elif 'account_help' in intents and action['id'].startswith('account_'):
                suggestions.append(action)
            elif 'billing' in intents and action['id'].startswith('payment_'):
                suggestions.append(action)
        
        return suggestions
