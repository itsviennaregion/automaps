import pytest

from automaps.confutils import get_config_value, get_default_args, has_config_option

import automapsconf


def test_has_config_option():
    assert has_config_option("myOption") == False
    automapsconf.myOption = "myValue"
    assert has_config_option("myOption") == True


def test_get_config_value():
    assert get_config_value("myOtherOption") == None
    assert get_config_value("myOtherOption", "defaultValue") == "defaultValue"
    automapsconf.myOtherOption = "myOtherValue"
    assert get_config_value("myOtherOption") == "myOtherValue"
    assert get_config_value("myOtherOption", "defaultValue") == "myOtherValue"


def test_get_default_args():
    def my_function(my_arg="default"):
        pass

    assert get_default_args(my_function)["my_arg"] == "default"
    assert len(get_default_args(my_function).keys()) == 1
    with pytest.raises(KeyError):
        get_default_args(my_function)["wrong_argument"]
