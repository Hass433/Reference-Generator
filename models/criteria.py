#models/criteria.py

from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator

class NumericCriteria(BaseModel):
    value: Union[int, float]
    operator: str = ">="

class CustomerCriteria(BaseModel):
    account_owner_text: Optional[str] = Field(None, description="Account owner")
    customer_name: Optional[str] = Field(None, description="Name of the customer")

    # Numeric fields with operator support
    invoice_volume: Optional[Union[int, NumericCriteria]] = Field(None, description="Invoice volume")
    po_percentage: Optional[Union[float, NumericCriteria]] = Field(None, description="Percentage of POs")
    non_po_percentage: Optional[Union[float, NumericCriteria]] = Field(None, description="Percentage of non-PO invoices")
    po_touchless_percentage: Optional[Union[float, NumericCriteria]] = Field(None, description="Percentage of touchless POs")
    automatic_distribution: Optional[Union[float, NumericCriteria]] = Field(None, description="Percentage of automatic distribution")

    erp_system: Optional[str] = Field(None, description="ERP system used by the customer")
    industry: Optional[str] = Field(None, description="Industry of the customer")
    product_activations: Optional[str] = Field(None, description="Product activations")
    account_url_link: Optional[str] = Field(None, description="Account URL link")

    limit: Optional[int] = Field(5, description="Number of results to return", gt=0, le=20)
    
    @validator('industry', 'erp_system', 'product_activations','account_url_link', pre=True)
    def lowercase_strings(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v
    
    @validator('invoice_volume', pre=True)
    def validate_invoice_volume(cls, v):
        if isinstance(v, dict) and "value" in v:
            value = v["value"]
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"Invoice volume must be a non-negative number, got {value}")
        elif v is not None and (not isinstance(v, (int, float)) or v < 0):
            raise ValueError(f"Invoice volume must be a non-negative number, got {v}")
        return v
    
    @validator('po_percentage', 'non_po_percentage', 'po_touchless_percentage', 'automatic_distribution', pre=True)
    def validate_percentages(cls, v):
        if isinstance(v, dict) and "value" in v:
            value = v["value"]
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ValueError(f"Percentage must be between 0 and 100, got {value}")
        elif v is not None and (not isinstance(v, (int, float)) or v < 0 or v > 100):
            raise ValueError(f"Percentage must be between 0 and 100, got {v}")
        return v
    
    @root_validator(pre=True)
    def convert_numeric_fields(cls, values):
        """Convert numeric fields to NumericCriteria objects if they're not already."""
        numeric_fields = ['invoice_volume', 'po_percentage', 'non_po_percentage', 
                         'po_touchless_percentage', 'automatic_distribution']
        
        for field in numeric_fields:
            if field in values:
                # Skip None values
                if values[field] is None:
                    continue
                    
                # Already in NumericCriteria format
                if isinstance(values[field], dict) and 'value' in values[field]:
                    # Keep it as is
                    pass
                else:
                    # Convert plain number to NumericCriteria
                    values[field] = {'value': values[field], 'operator': '>='}
        
        return values
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method for better serialization for logging."""
        result = super().dict(*args, **kwargs)
        
        # Format numeric criteria fields for better logging
        numeric_fields = ['invoice_volume', 'po_percentage', 'non_po_percentage', 
                         'po_touchless_percentage', 'automatic_distribution']
        
        for field in numeric_fields:
            if field in result and result[field] is not None:
                if isinstance(result[field], dict) and 'value' in result[field] and 'operator' in result[field]:
                    op = result[field]['operator']
                    val = result[field]['value']
                    # Format like "< 10000" for logging
                    result[field] = f"{op} {val}"
        
        return result