def get_data_value(data, key):
    if isinstance(data, dict):
        return data[key]

    return getattr(data, key)
