from functools import wraps
from dataclasses import is_dataclass

def trim(cls):
    original_init = cls.__init__

    @wraps(original_init)
    def new_init(self, **kwargs):
        processed_kwargs = trimData(kwargs, cls)
        original_init(self, **processed_kwargs)

    cls.__init__ = new_init
    return cls

def trimData(json_data: dict, cls: type) -> dict:
    if is_dataclass(cls):
        return {key: value for key, value in json_data.items() if key in cls.__dataclass_fields__}
    else:
        return {key: value for key, value in json_data.items() if key in cls.__annotations__}
