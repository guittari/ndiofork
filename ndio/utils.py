import simplejson as json
import uuid
import time
from bson import json_util

def json_compat_wrap(obj):
    """
    Convert a datetime object to a string.

    Args:
        obj (object): The object to convert.

    Returns:
        object: The converted object.

    Examples:
        >>> json_compat_wrap(datetime.datetime(2020, 1, 1))
        '2020-01-01T00:00:00'
    """
    return json.loads(json_util.dumps(obj))
    
def create_new_sortable_unique_id() -> str:
    """
    Create a new unique ID that is sortable by time.

    Note that while the time component is currently implemented as the number
    of milliseconds since the epoch, this is not guaranteed to be the case in
    the future. The only guarantee is that the IDs will be sortable by time
    among all IDs created by the same version of the function.

    This function is therefore prefixed with the slug "sidv1" to indicate that
    it is a sortable ID version 1. This is to allow for future versions of the
    function that may use a different time component.

    Returns:
        str: A new unique ID.

    Examples:
        >>> id1 = create_new_sortable_unique_id()
        >>> id2 = create_new_sortable_unique_id()
        >>> id1 < id2
        True
    """
    return f"sidv1-{int(time.time()*1000)}-{uuid.uuid4()}"


def table_name_to_type_name(table_name: str) -> str:
    """
    Convert a table name like "collections" to a type name like "Collection".

    * De-pluralize
    * Capitalize first letter

    Args:
        table_name (str): The table name.

    Returns:
        str: The type name.

    Examples:
        >>> table_name_to_type_name("collections")
        'Collection'

    """
    return table_name.rstrip("s").capitalize()


def type_name_to_table_name(type_name: str) -> str:
    """
    Convert a type name like "Collection" to a table name like "collections".

    * De-capitalize first letter
    * Pluralize

    Args:
        type_name (str): The type name.

    Returns:
        str: The table name.

    Examples:
        >>> type_name_to_table_name("Collection")
        'collections'

    """
    return type_name[0].lower() + type_name[1:] + "s"


def get_schema_for_table(table: dict) -> dict:
    """
    Generate a JSONSchema object for a table.

    Args:
        table (dict): The table.

    Returns:
        dict: The JSONSchema object.

    Examples:
        >>> get_schema_for_table({"name": "Collection", "columns": [{"name": "name", "type": "string"}]})
        {'$schema': 'http://json-schema.org/draft-07/schema#', 'type': 'object', 'properties': {'name': {'type': 'string'}}}
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            column: {"type": table["data"][column].dtype.name}
            for column in table["columns"]
        },
    }


__all__ = [
    "create_new_sortable_unique_id",
    "table_name_to_type_name",
    "type_name_to_table_name",
    "get_schema_for_table",
    "json_compat_wrap",
]
