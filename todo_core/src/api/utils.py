def str_to_bool(value):
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes']
    return bool(value)
