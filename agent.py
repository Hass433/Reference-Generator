import streamlit as st
import pandas as pd
from services.parser import parse_criteria
from services.query_builder import build_soql_query
from services.query_executor import query_salesforce
from utils.formatter import format_results, get_formatted_dataframe
from utils.logger import logger
from typing import List, Dict, Tuple, Union

def customer_reference_agent(prompt: str) -> Tuple[Union[str, pd.DataFrame], List[Dict], str]:
    """Core agent function that returns formatted results, raw data, and SOQL query"""
    logger.info(f"Processing prompt: '{prompt}'")
    criteria = parse_criteria(prompt)
    soql_query = build_soql_query(criteria)
    results = query_salesforce(soql_query)
    
    if not results:
        return "No customers found matching your criteria.", [], soql_query
    else:
        return format_results(results), results, soql_query

def display_chat_message(role: str, content: Union[str, pd.DataFrame], expandable_content: str = None):
    """Display a chat message with optional expandable content"""
    with st.chat_message(role):
        # Handle "no results" case
        if content == "No customers found matching your criteria.":
            st.warning(content)
            if expandable_content:
                with st.expander("View Query Details"):
                    st.code(expandable_content, language="sql")
            return
            
        # Handle DataFrame case
        if isinstance(content, pd.DataFrame):
            if not content.empty:
                st.dataframe(content, use_container_width=True)
                if expandable_content:
                    with st.expander("View Query Details"):
                        st.code(expandable_content, language="sql")
            return
            
        # Handle string messages (fallback)
        st.markdown(content)
        if expandable_content:
            with st.expander("View Query Details"):
                st.code(expandable_content, language="sql")

def get_capabilities_message() -> str:
    """Generate dynamic capabilities message"""
    return (
        "🔍 **I can retrieve customer data from Salesforce based on:**\n\n"
        "- **PO automation levels** (po touchless %, PO %, non-PO %, Automatic distribution %)\n"
        "- **Invoice volumes** (eg. at least 10000 invoices)\n"
        "- **ERP systems** (eg. Oracle, MS Dynamics...)\n"
        "- **Product activations** (eg. Readsoft Invoices, Connect BC Cloud, ...)\n\n"
        "- **Industry sectors** (eg. Manufacturing, Retail, Consumer Products...)\n\n"
        "💡 **Example queries:**\n"
        "> _'Show me 5 retail customers with less than 30% po touchless and more than 10k invoices'_\n"
    )

def get_general_response(prompt: str) -> str:
    """Handle general non-data questions"""
    prompt_lower = prompt.lower()
    
    greetings = ["hi", "hello", "hey", "greetings"]
    if any(word in prompt_lower for word in greetings):
        return f"👋 Hello! I'm your Customer Reference Assistant. How can I help you today?\n\n{get_capabilities_message()}"
    
    help_phrases = ["help", "what can you do", "capabilities", "assistance"]
    if any(phrase in prompt_lower for phrase in help_phrases):
        return get_capabilities_message()
    
    about_phrases = ["who are you", "what are you", "your purpose"]
    if any(phrase in prompt_lower for phrase in about_phrases):
        return ("🤖 I'm an AI-powered Customer Reference Assistant. "
                "My purpose is to help you find relevant customer references "
                "based on various criteria like industry, ERP systems, and automation metrics.")
    
    return None

def is_data_query(prompt: str) -> bool:
    """Determine if the prompt is asking for customer data"""
    prompt_lower = prompt.lower()
    
    # Check for data-related keywords
    data_keywords = [
        "customer", "client", "reference", "find", "show", "list",
        "industry", "erp", "invoice", "volume", "percentage", 
        "po", "non-po", "touchless", "automation", "activation"
    ]
    
    return any(keyword in prompt_lower for keyword in data_keywords)

def initialize_session_state():
    """Initialize or reset session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.raw_results = {}
        st.session_state.soql_queries = {}
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"👋 Hi! I'm your Customer Reference Assistant.\n\n{get_capabilities_message()}"
        })

def main():
    st.set_page_config(
        page_title="Customer Reference Assistant",
        page_icon="💬",
        layout="centered"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Clear chat button in sidebar
    with st.sidebar:
        if st.button("🧹 Clear Conversation", use_container_width=True, type="primary"):
            st.session_state.clear()
            initialize_session_state()
            st.rerun()
    
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        # For assistant messages with stored queries, show expandable content
        expandable = st.session_state.soql_queries.get(i)
        display_chat_message(
            message["role"], 
            message["content"],
            expandable_content=expandable
        )
    
    # Chat input
    if prompt := st.chat_input("Ask about customer references..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("🔍 Searching customer references..."):
            try:
                # First check for general questions
                general_response = get_general_response(prompt)
                if general_response is not None:
                    response = general_response
                    soql_query = None
                # Then check if it's a data query
                elif is_data_query(prompt):
                    # Process data query
                    formatted_results, raw_results, soql_query = customer_reference_agent(prompt)
                    response = formatted_results
                    
                    # Store raw data and query for this message index
                    idx = len(st.session_state.messages)
                    st.session_state.raw_results[idx] = raw_results
                    st.session_state.soql_queries[idx] = soql_query
                else:
                    # Default response for unrecognized queries
                    response = (
                        "🤔 I'm not sure I understand your request. \n\n"
                        "I can help you find customer references based on various criteria. "
                        "Try asking something like:\n"
                        "> 'Show me manufacturing customers with high PO automation'\n"
                        "> 'Find clients using SAP with over 10,000 invoices'\n\n"
                        "Or ask 'What can you do?' to see my capabilities."
                    )
                    soql_query = None
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
                
                # Rerun to update display
                st.rerun()
                
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}", exc_info=True)
                error_msg = (
                    "⚠️ **Sorry, I encountered an error processing your request.**\n\n"
                    "Please try:\n"
                    "- Rephrasing your query\n"
                    "- Using simpler criteria\n"
                    "- Contacting support if the issue persists"
                )
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })
                st.rerun()

if __name__ == "__main__":
    main()