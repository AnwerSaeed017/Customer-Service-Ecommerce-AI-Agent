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
