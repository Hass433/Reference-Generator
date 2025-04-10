import logging
from datetime import datetime
import json
from typing import Any, Dict

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'customer_reference_agent_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

def log_json(data: Dict[str, Any], step_name: str):
    """Helper function to log JSON data with pretty formatting"""
    logger.info(f"{step_name} JSON:\n{json.dumps(data, indent=2)}")