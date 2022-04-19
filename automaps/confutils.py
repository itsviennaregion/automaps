import inspect

from typing import Any, Generic, Union


def check_config_options():
    import automapsconf
    import automaps.automapsconf

    for option, type_ in automaps.automapsconf.__annotations__.items():
        print("\n", option, type_)
        if hasattr(type_, "__args__"):
            print(type_.__dict__)
            print(type_.__args__)

        # option not found in config
        if option not in automapsconf.__dict__:
            # but is optional
            assert type(None) in type_.__args__
        # simple type
        elif not hasattr(type_, "__args__"):
            assert isinstance(automapsconf.__dict__[option], type_)
        # type from typing
        elif hasattr(type_, "__origin__"):
            # Union type
            if type_.__origin__ == Union:
                # config option has one of the united types
                assert type(automapsconf.__dict__[option]) in type_.__args__
            else:  # Container
                assert isinstance(automapsconf.__dict__[option], type_.__origin__)


def has_config_option(config_option: str) -> bool:
    import automapsconf

    return hasattr(automapsconf, config_option)


def get_config_value(config_option: str, default_value: Any = None) -> Any:
    import automapsconf

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
