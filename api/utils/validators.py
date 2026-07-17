import re

def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r'[^\d+]', '', phone or '')
    return cleaned