FIELD_MAPPING = {
    "tenant": "tenant__c",
    "account_owner": "Account__r.Account_Owner_TEXT__c",


    "invoice_volume": "archived_invoice_count_R12__c",
    "po_percentage": "po_I_E_Percent__c", #po_share_total_invoice_volume
    "non_po_percentage": "non_po_I_E_percent__c", #non_po_share_total_invoice_volume
    "po_touchless_percentage": "po_Touchless_Percent__c",
    "automatic_distribution": "Automatic_distribution_percent__c",


    "industry": "Account__r.Industry",
    "erp_system": "Account__r.ERP__c",
    "product_activations": "Account__r.Product_Activations__c",
    "account_url_link": "Account__r.Account_URL_Link__c",

    "is_latest": "IsLatest__c",
    "customer_type": "Account__r.Type"



}