"""Customer lookup for the ticket graph.

A JSON file stands in for a real customer database.
"""
import json
from pathlib import Path

# src/scoutbot/tools.py -> project root -> seed/
CUSTOMERS_PATH = Path(__file__).resolve().parents[2] / "seed" / "mock_customers.json"


def look_up_customer(customer_id: str) -> dict:
    ''' Return the customer's record, or {"found": False} if the ID is unknown. '''
    customers = json.loads(CUSTOMERS_PATH.read_text())
    record = customers.get(customer_id)
    if record is None:
        return {"found": False, "customer_id": customer_id}
    return {"found": True, **record}
