from config.field_mapping import FIELD_MAPPING
from models.criteria import CustomerCriteria,NumericCriteria  
from utils.logger import logger, log_json 

def build_soql_query(criteria: CustomerCriteria) -> str:
    logger.info("Starting SOQL query building")
    log_json(criteria.dict(), "Input criteria for query building")
    
    base_query = f"""
    SELECT {', '.join(FIELD_MAPPING.values())}
    FROM Usage_statistic__c
    WHERE {FIELD_MAPPING['is_latest']} = true
    AND {FIELD_MAPPING['type_customer']} = 'Client'
    """
    
    conditions = []
    
    # Handle string fields
    if criteria.account_owner_text is not None:
        conditions.append(f"{FIELD_MAPPING['account_owner_text']} LIKE '%{criteria.account_owner_text}%'")
    if criteria.tenant is not None:
        conditions.append(f"{FIELD_MAPPING['tenant']} LIKE '%{criteria.tenant}%'")
    if criteria.industry is not None:
        conditions.append(f"{FIELD_MAPPING['industry']} LIKE '%{criteria.industry}%'")
    if criteria.erp_system:
        conditions.append(f"{FIELD_MAPPING['erp_system']} INCLUDES ('{criteria.erp_system}')")
    if criteria.product_activations:
        conditions.append(f"{FIELD_MAPPING['product_activations']} INCLUDES ('{criteria.product_activations}')")
    
    # Handle numeric fields with their respective operators
    numeric_fields = [
        ('invoice_volume', 'invoice_volume'),
        ('po_percentage', 'po_percentage'),
        ('non_po_percentage', 'non_po_percentage'),
        ('po_touchless_percentage', 'po_touchless_percentage'),
        ('automatic_distribution', 'automatic_distribution')
    ]
    
    for attr_name, field_name in numeric_fields:
        attr_value = getattr(criteria, attr_name)
        if attr_value is None:
            continue
            
        if isinstance(attr_value, NumericCriteria):
            value = attr_value.value
            operator = attr_value.operator
        else:
            value = attr_value
            operator = ">="  # Default operator
        
        conditions.append(f"{FIELD_MAPPING[field_name]} {operator} {value}")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += f" LIMIT {criteria.limit}"
    
    logger.info(f"Final SOQL query:\n{base_query}")
    return base_query