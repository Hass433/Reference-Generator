#utils/formatter.py
from config.field_mapping import FIELD_MAPPING
import pandas as pd

def get_nested_value(data: dict, field_path: str, default="N/A"):
    """Get nested field values using dot notation"""
    keys = field_path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, default)
        else:
            return default
    return value if value is not None else default

def format_results(results: list[dict]) -> str:
    if not results:
        return "No customers found matching your criteria."
    
    # Prepare data for DataFrame
    formatted_data = []
    
    for customer in results:
        formatted_data.append({
            "Customer Name": get_nested_value(customer, FIELD_MAPPING['customer_name']),
            "Account Owner": get_nested_value(customer, FIELD_MAPPING['account_owner']),
            "Industry": get_nested_value(customer, FIELD_MAPPING['industry']),
            "PO %": f"{get_nested_value(customer, FIELD_MAPPING['po_percentage'])}%",
            "Non-PO %": f"{get_nested_value(customer, FIELD_MAPPING['non_po_percentage'])}%",
            "PO Touchless %": f"{get_nested_value(customer, FIELD_MAPPING['po_touchless_percentage'])}%",
            "Auto Dist %": f"{get_nested_value(customer, FIELD_MAPPING['automatic_distribution'])}%",
            "Invoice Volume": get_nested_value(customer, FIELD_MAPPING['invoice_volume']),
            "ERP System": get_nested_value(customer, FIELD_MAPPING['erp_system']),
            "Product Activations": get_nested_value(customer, FIELD_MAPPING['product_activations']),
            "Account URL": get_nested_value(customer, FIELD_MAPPING['account_url_link'])
        })
    
    # Create DataFrame
    df = pd.DataFrame(formatted_data)
    
    # Format DataFrame
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_colwidth', 30)
    
    # Return formatted DataFrame as string
    return df.to_string(index=False)

def format_results_html(results: list[dict]) -> str:
    if not results:
        return "No customers found matching your criteria."
    
    # Create DataFrame as above
    formatted_data = []
    for customer in results:
        formatted_data.append({
            "Customer Name": get_nested_value(customer, FIELD_MAPPING['customer_name']),
            "Account Owner": get_nested_value(customer, FIELD_MAPPING['account_owner']),
            "Industry": get_nested_value(customer, FIELD_MAPPING['industry']),
            "PO %": f"{get_nested_value(customer, FIELD_MAPPING['po_percentage'])}%",
            "Non-PO %": f"{get_nested_value(customer, FIELD_MAPPING['non_po_percentage'])}%",
            "PO Touchless %": f"{get_nested_value(customer, FIELD_MAPPING['po_touchless_percentage'])}%",
            "Auto Dist %": f"{get_nested_value(customer, FIELD_MAPPING['automatic_distribution'])}%",
            "Invoice Volume": get_nested_value(customer, FIELD_MAPPING['invoice_volume']),
            "ERP System": get_nested_value(customer, FIELD_MAPPING['erp_system']),
            "Product Activations": get_nested_value(customer, FIELD_MAPPING['product_activations']),
            "Account URL": get_nested_value(customer, FIELD_MAPPING['account_url_link'])
        })
    
    df = pd.DataFrame(formatted_data)
    
    # Return styled HTML table
    return df.to_html(
        index=False,
        classes="table table-striped table-hover",
        border=0
    )

def get_formatted_dataframe(results: list[dict]) -> pd.DataFrame:
    """Return data as a pandas DataFrame for direct use in Streamlit"""
    if not results:
        return pd.DataFrame()  # Empty DataFrame
    
    formatted_data = []
    for customer in results:
        formatted_data.append({
            "Customer Name": get_nested_value(customer, FIELD_MAPPING['customer_name']),
            "Account Owner": get_nested_value(customer, FIELD_MAPPING['account_owner']),
            "Industry": get_nested_value(customer, FIELD_MAPPING['industry']),
            "PO %": f"{get_nested_value(customer, FIELD_MAPPING['po_percentage'])}%",
            "Non-PO %": f"{get_nested_value(customer, FIELD_MAPPING['non_po_percentage'])}%",
            "PO Touchless %": f"{get_nested_value(customer, FIELD_MAPPING['po_touchless_percentage'])}%",
            "Auto Dist %": f"{get_nested_value(customer, FIELD_MAPPING['automatic_distribution'])}%",
            "Invoice Volume": get_nested_value(customer, FIELD_MAPPING['invoice_volume']),
            "ERP System": get_nested_value(customer, FIELD_MAPPING['erp_system']),
            "Product Activations": get_nested_value(customer, FIELD_MAPPING['product_activations']),
            "Account URL": get_nested_value(customer, FIELD_MAPPING['account_url_link'])
        })
    
    return pd.DataFrame(formatted_data)