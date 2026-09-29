"""
This module contains helper functions that are used all throughout the mosaic_client library.
"""

from typing import Any

import zeep.helpers
from zeep import Client


def _serialize_dict(obj: Any) -> Any:
    """
    Converts a zeep response object into a dict or list, depending on the structure of the
    response data.

    :param obj: object to convert
    :return: object as dict or list
    """
    return zeep.helpers.serialize_object(obj, dict)


def _malformed_key_value_response(reason: str) -> ValueError:
    """
    Returns a ValueError informing about an incorrectly structured key-value response.

    :param reason: reason for error
    :return: ValueError with specified reason
    """
    return ValueError(f"key-value response is malformed: {reason}")


def _read_key_value_list(entry_list: list) -> list[tuple[Any, Any]]:
    """
    Reads a list of objects structured as [{ "key", "value" }] into a list of tuples
    where the first value of the tuple is the key and the second is the value. This function
    will throw a ValueError if the list passed into this function is malformed.

    :param entry_list: list of objects to parse
    :return: list of key-value tuples
    """
    key_value_lst: list[tuple[Any, Any]] = []

    for i in range(len(entry_list)):
        entry = entry_list[i]

        # check for "key" key
        if "key" not in entry:
            raise _malformed_key_value_response(f"'entry[{i}]' is missing 'key' attribute")

        # check for "value" key
        if "value" not in entry:
            raise _malformed_key_value_response(f"'entry[{i}]' is missing 'value' attribute")

        key_value_lst.append((entry["key"], entry["value"]))

    return key_value_lst


def _read_key_value_entry_response(response: Any) -> list[tuple[Any, Any]]:
    """
    Reads an object structured as { "entry": [{ "key", "value" }] } into a list of tuples
    where the first value of the tuple is the key and the second is the value. This function
    will throw a ValueError if the object passed into this function is malformed.

    :param response: object to parse
    :return: list of key-value tuples
    """
    # check that it's actually a dict
    if type(response) != dict:
        raise _malformed_key_value_response("not an object")

    # check for "entry" key
    if "entry" not in response:
        raise _malformed_key_value_response("'entry' attribute is missing")

    # "entry" key should hold list of key-value entries
    response_entry_lst = response["entry"]

    # check that it's actually a list
    if type(response_entry_lst) != list:
        raise _malformed_key_value_response("'entry' value is not a list")

    return _read_key_value_list(response_entry_lst)


def _cast_client(client: Client | str) -> Client:
    """
    Takes zeep client instances or wsdl urls as strings and either just returns the given client instance or creates
    one if a string was given. Raises a TypeError if the given client is neither a zeep client nor a string.

    :param client: client instance or wsdl url as a string
    :return: zeep client instance
    """
    if isinstance(client, Client):
        pass
    elif isinstance(client, str):
        client = Client(client)
    else:
        raise TypeError(f"unsupported constructor argument type: {type(client)}")

    return client


class WSDLClient:
    """
    Generic SOAP client base.
    """

    def __init__(self, client: Client | str):
        """
        Constructs a new SOAP client.

        :param client: URL to WSDL endpoint or zeep instance with WSDL information
        """
        self._client = _cast_client(client)
