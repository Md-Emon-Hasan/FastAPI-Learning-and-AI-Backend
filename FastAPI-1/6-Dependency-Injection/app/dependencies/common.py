from typing import List, Dict

# fake in-memory DB
FAKE_DB: List[Dict] = []

def get_db():
    """
    Acts like a database session.
    Later: replaced by real DB session
    """
    return FAKE_DB
