WALLET_TOP_UP_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string"},
        "currency": {"type": "string"},
    },
    "required": ["value", "currency"],
}

TRANSACTION_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "to_name": {"type": "string"},
        "value": {"type": "string"},
        "currency": {"type": "string"},
    },
    "required": ["to_name", "value", "currency"],
}

