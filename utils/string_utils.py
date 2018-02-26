def empty_to_none(s):
    """
    :param s: String to be converted.
    :return: If string is empty returns None; otherwise returns string itself.
    """
    if s is not None:
        if len(s) == 0:
            return None
    return s

