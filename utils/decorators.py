from functools import wraps

def trim(cls):
    original_init = cls.__init__

    @wraps(original_init)
    def new_init(self, **kwargs):
        processed_kwargs = trimData(kwargs, cls)
        original_init(self, **processed_kwargs)

    cls.__init__ = new_init
    return cls

def trimData(json_data: dict, cls: type) -> dict:
    return {key: value for key, value in json_data.items() if key in cls.__annotations__}
