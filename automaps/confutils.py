import automapsconf

def has_config_option(config_option: str) -> bool:
    return hasattr(automapsconf, config_option) and getattr(automapsconf, config_option)