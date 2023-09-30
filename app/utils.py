def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flattens a nested dictionary and uses a separator (default is '.')
    to denote levels of nesting in the returned flat dictionary.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def unflatten_dict(d: dict, sep: str = ".") -> dict:
    """
    Reconstructs a nested dictionary from a flat dictionary
    that used a separator (default is '.') to denote levels of nesting.
    """
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        res = result
        for k in keys[:-1]:
            res = res.setdefault(k, {})
        res[keys[-1]] = value

    return result
