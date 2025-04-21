from typing import Dict, Any, List, Optional
import json
import difflib
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI
from models.criteria import CustomerCriteria
from config.settings import settings
from utils.logger import logger, log_json  
from config.static_lists import ERP_SYSTEMS, INDUSTRIES, PRODUCT_ACTIVATIONS


llm = AzureChatOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
    temperature=0
)

def find_best_match(input_value: str, possible_values: List[str]) -> Optional[str]:
    """Find the best match for the input value in the list of possible values."""
    if not input_value or not possible_values:
        return None
        
    # Convert input to lowercase for case-insensitive matching
    input_lower = input_value.lower()
    
    # Try exact match first (case insensitive)
    for value in possible_values:
        if value.lower() == input_lower:
            return value
    
    # Try to find the closest match
    matches = difflib.get_close_matches(input_lower, [v.lower() for v in possible_values], n=1, cutoff=0.8)
    if matches:
        # Find the original case version
        match_index = [v.lower() for v in possible_values].index(matches[0])
        return possible_values[match_index]
    
    return None

def clean_json_response(response: str) -> Dict[str, Any]:
    """Clean the JSON response by removing markdown code blocks."""
    logger.info(f"Raw LLM response:\n{response}")
    
    if response.startswith('```json') and response.endswith('```'):
        response = response[7:-3].strip()
    elif response.startswith('```') and response.endswith('```'):
        response = response[3:-3].strip()
    
    logger.info(f"Cleaned JSON string:\n{response}")
    return json.loads(response)

def parse_criteria(prompt: str) -> CustomerCriteria:
    logger.info(f"Starting criteria parsing for prompt: '{prompt}'")
    
    parser_prompt = ChatPromptTemplate.from_template("""
    Extract the following parameters from the user's request. Return only a JSON object with the extracted values.
    
    For numeric parameters (invoice_volume, po_percentage, non_po_percentage, po_touchless_percentage, automatic_distribution), 
    determine if the user wants:
    - Exact equality: If they use phrases like "exactly", "equal to", "is", etc.
    - Less than: If they use phrases like "less than", "below", "under", etc.
    - Less than or equal: If they use phrases like "at most", "maximum", etc.
    - Greater than: If they use phrases like "more than", "above", "over", etc.
    - Greater than or equal: If they use phrases like "at least", "minimum", etc.
    
    For these numeric fields, return an object with:
    - "value": The numeric value
    - "operator": One of "=", "<", "<=", ">", ">=" based on the user's intent
    
    Parameters to extract:
    - account_owner_text: Account owner name
    - tenant: Name of the customer
    - invoice_volume: Invoice volume with comparison operator
    - po_percentage: Percentage of POs with comparison operator (0-100)
    - non_po_percentage: Percentage of non-PO invoices with comparison operator (0-100)
    - po_touchless_percentage: Percentage of touchless POs with comparison operator (0-100)
    - automatic_distribution: Percentage of automatic distribution with comparison operator (0-100)
    - erp_system: The ERP system used by the customer
    - industry: The industry of the customer (e.g., manufacturing, retail)
    - product_activations: Product activations
    - limit: Number of results to return (default 5, max 20)
    
    Return ONLY valid JSON. Do not include any additional text or explanation.
    
    Example output format for numeric fields:
    "invoice_volume": {{"value": 1000, "operator": ">="}}
    "po_percentage": {{"value": 50, "operator": "="}}
    
    User request: {prompt}
    """)
    
    parser_chain = parser_prompt | llm | StrOutputParser()
    json_response = parser_chain.invoke({"prompt": prompt})
    
    try:
        json_data = clean_json_response(json_response)
        log_json(json_data, "Parsed criteria")
        
        # Apply fuzzy matching to ERP system, industry, and product activations
        if 'erp_system' in json_data and json_data['erp_system']:
            best_match = find_best_match(json_data['erp_system'], ERP_SYSTEMS)
            if best_match:
                json_data['erp_system'] = best_match
                logger.info(f"Mapped ERP system to '{best_match}'")
            else:
                logger.warning(f"No close match found for ERP system '{json_data['erp_system']}'")
        
        if 'industry' in json_data and json_data['industry']:
            best_match = find_best_match(json_data['industry'], INDUSTRIES)
            if best_match:
                json_data['industry'] = best_match
                logger.info(f"Mapped industry to '{best_match}'")
            else:
                logger.warning(f"No close match found for industry '{json_data['industry']}'")
        
        if 'product_activations' in json_data and json_data['product_activations']:
            best_match = find_best_match(json_data['product_activations'], PRODUCT_ACTIVATIONS)
            if best_match:
                json_data['product_activations'] = best_match
                logger.info(f"Mapped product activations to '{best_match}'")
            else:
                logger.warning(f"No close match found for product activations '{json_data['product_activations']}'")
        
        criteria = CustomerCriteria(**json_data)
        logger.info(f"Successfully created criteria object: {criteria}")
        return criteria
    except Exception as e:
        logger.error(f"Error parsing criteria: {e}\nRaw response: {json_response}")
        return CustomerCriteria()