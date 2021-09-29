import inspect
from typing import Any

import automapsconf


def has_config_option(config_option: str) -> bool:
    return hasattr(automapsconf, config_option)


def get_config_value(config_option: str, default_value: Any = None) -> Any:
    if has_config_option(config_option):
        return getattr(automapsconf, config_option)
    elif default_value:
        return default_value
    else:
        return None


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
