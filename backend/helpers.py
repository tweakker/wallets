from json import loads


def json_decoder(s, *args, **kwargs):
    """Patched json decoder."""
    if s is None:
        s = {}
    return loads(s, *args, **kwargs)
