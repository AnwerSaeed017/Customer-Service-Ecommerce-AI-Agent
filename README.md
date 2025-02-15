# Customer-Service-Ecommerce-AI-Agent

A Customer Service Ecommerce AI Agent built using Langgraph, Langchain, Mistral7B, and a Streamlit UI.

## Overview

This project is an AI-powered customer service agent designed specifically for ecommerce support. The agent leverages advanced technologies—Langgraph, Langchain, Mistral7B, and Streamlit—to handle customer inquiries, verify identities, manage orders, and execute various actions. It is ideal for providing responsive, automated customer support while seamlessly integrating with backend services.

## Features

- **Identity Verification:** Securely verify customer credentials before processing sensitive requests.
- **Order Management:** 
  - Track order status
  - Update shipping addresses
  - Request refunds
  - Send order details via email
- **General Support:** 
  - Provide product information, shipping policies, and return policies
  - Assist with technical issues
- **Real-time Updates:** Keep customers informed with timely order status notifications and shipping updates.
- **AI-Driven Conversations:** Utilize a custom AI agent (MetaCSRAgent) to generate context-aware responses.
- **Workflow Management:** A state-driven workflow (MetaCSRWorkflow) that directs the conversation through various service stages.
- **Feedback Collection:** Automatically collect and log customer feedback, with the option to escalate to human support if necessary.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies

You can install all the required packages using the following command:

```bash
pip install streamlit python-dotenv langchain langchain-groq langgraph
```

### Project Structure
app.py:
The main entry point for the Streamlit application that sets up the user interface and handles session management.

agents/
Contains the AI agent implementation (csr_agent.py) responsible for generating responses and processing customer messages.

graph/
Houses the workflow management logic (workflow.py) that defines the state transitions for customer service interactions.

models/
Contains the state definitions (state.py) for tracking conversation context and workflow status.

tools/
Provides utility functions (tools.py) to perform various tasks such as verifying identities, fetching order statuses, updating shipping addresses, and more.

.env:
An environment file for storing Groq api key.

### Code Overview
MetaCSRApp:
Manages the UI components (header, sidebar, chat interface) and user session states. It integrates the workflow and agent to drive the conversation.

MetaCSRAgent:
Implements the core AI functionality:

Sentiment Analysis & Intent Determination: Adjusts response tone and suggests actions based on user input.
Response Generation: Uses a predefined prompt and an underlying language model (via ChatGroq) to generate customer responses.
Action Suggestions: Proposes next steps based on the analysis of the conversation.
MetaCSRWorkflow:
Controls the conversation flow:

Identity Verification Node: Validates user credentials.
Query Processing Node: Determines the next action based on the user's request.
Action Execution Node: Executes pending actions (e.g., updating shipping details).
Feedback Collection Node: Gathers user feedback when needed.
Final Node: Marks the conversation's conclusion.
Tools (tools.py):
A dedicated module that provides various helper functions for the agent:

Implements a unified tools class (MetaCSRTools) to handle API (or mock API) interactions.
Provides decorated standalone functions (using @tool) for verifying identity, querying a knowledge base, fetching order status, updating shipping addresses, requesting refunds, sending order emails, updating account details, scheduling callbacks, and logging feedback.
These tools encapsulate the logic for interacting with external systems or services, streamlining the agent's operations.
