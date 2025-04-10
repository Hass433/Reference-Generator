import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Salesforce credentials
    SALESFORCE_USERNAME = st.secrets["SALESFORCE_USERNAME"]
    SALESFORCE_PASSWORD = st.secrets["SALESFORCE_PASSWORD"]
    SALESFORCE_SECURITY_TOKEN = st.secrets["SALESFORCE_SECURITY_TOKEN"]
    SALESFORCE_DOMAIN = st.secrets.get("SALESFORCE_DOMAIN", "login")
    
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
    AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
    AZURE_OPENAI_DEPLOYMENT = st.secrets["AZURE_OPENAI_DEPLOYMENT"]
    AZURE_OPENAI_API_VERSION = st.secrets["AZURE_OPENAI_API_VERSION"]
    
    # Default query limits
    DEFAULT_RESULT_LIMIT = 5
    MAX_RESULT_LIMIT = 20

settings = Settings()
