from typing import List, Dict
from langchain_salesforce import SalesforceTool
from config.settings import settings
from utils.logger import logger, log_json  

salesforce_tool = SalesforceTool(
    username=settings.SALESFORCE_USERNAME,
    password=settings.SALESFORCE_PASSWORD,
    security_token=settings.SALESFORCE_SECURITY_TOKEN,
    domain=settings.SALESFORCE_DOMAIN
)

def query_salesforce(soql_query: str) -> List[Dict]:
    logger.info(f"Executing Salesforce query: {soql_query}")
    
    try:
        result = salesforce_tool.run({
            "operation": "query",
            "query": soql_query
        })
        
        logger.info("Raw Salesforce response received")
        log_json(result, "Salesforce raw response")
        
        # Ensure we're returning a list of records
        if isinstance(result, dict) and 'records' in result:
            logger.info(f"Found {len(result['records'])} records")
            return result['records']
        elif isinstance(result, list):
            logger.info(f"Found {len(result)} records")
            return result
        else:
            logger.warning(f"Unexpected Salesforce response format: {type(result)}")
            return []
    except Exception as e:
        logger.error(f"Error querying Salesforce: {str(e)}")
        return []