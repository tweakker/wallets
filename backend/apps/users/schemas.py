USER_LOGIN_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "password": {"type": "string"},
    },
    "required": ["name", "password"],
}
