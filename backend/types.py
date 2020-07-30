import typing as t


JSONValue = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
JSON = t.Union[t.Dict[str, JSONValue], t.List[JSONValue]]
