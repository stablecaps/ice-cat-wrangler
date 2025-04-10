def safeget(dct, *keys):
    """
    Recover value safely from nested dictionary

    safeget(example_dict, 'key1', 'key2')
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct
