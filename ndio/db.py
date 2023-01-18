import os
from typing import Tuple
import pandas as pd
from pymongo import MongoClient
from pymongo.database import Database



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


__all__ = [
    "create_new_sortable_unique_id",
    "table_name_to_type_name",
    "type_name_to_table_name",
    "get_schema_for_table",
    "json_compat_wrap",
]




def ingest_from_xlsx(db, xlsx_file_path: str, delete_existing: bool = True) -> None:
    """
    Ingest data from an Excel file into the database.

    For sanity, I'm going to call the different sheets "tables" in the database
    so that they won't be confused with the "Collection" data object. When we
    access these, we'll always talk about the tables as "collections" as they
    are meant to be called.

    Args:
        xlsx_file_path (str): The path to the Excel file to ingest.

    Returns:
        None

    Examples:
        >>> ingest_from_xlsx("test.xlsx")
    """

    xlsx = pd.read_excel(xlsx_file_path, sheet_name=None, engine="openpyxl")
    # Get the sheet names from the Excel file
    sheet_names = list(xlsx.keys())

    tables = {}
    # We will populate this so that each item looks like:
    # tables = {
    #     "collections": {
    #         "name": "collections",
    #         "type_name": "Collection",
    #         "data": pd.DataFrame,
    #         "columns": list[str]
    #     },
    #     ...
    # }
    # Iterate over the sheets in the Excel file and populate the tables dict.
    for sheet_name in sheet_names:
        df = xlsx[sheet_name]
        tables[sheet_name.lower()] = {  # type: ignore
            "name": sheet_name.lower(),  # type: ignore
            "type_name": table_name_to_type_name(sheet_name),  # type: ignore
            "data": df,
            "columns": list(df.columns),
        }

    # First upsert entries in the "schemas" col in the database.
    # This will be a list of dicts, each dict representing a table.
    # Each dict will have the following keys:
    #   - name: The name of the table.
    #   - type_name: The name of the type that represents the table.
    #   - schema: A JSON-schema for the columns in the table.

    # Make sure the "schemas" coll exists in the database.
    if "schemas" not in db.list_collection_names():
        db.create_collection("schemas")

    # Get the "schemas" collection.
    schemas = db["schemas"]

    # Iterate over the tables and upsert the schemas.
    for table_name, table in tables.items():
        # Get the schema for the table.
        schema = get_schema_for_table(table)
        # Upsert the schema.
        schemas.update_one(
            {"name": table_name},
            {
                "$set": {
                    "name": table_name,
                    "type_name": table["type_name"],
                    "schema": schema,
                }
            },
            upsert=True,
        )

    # Now we need to upsert the data in the tables.
    # Iterate over the tables and upsert the data.
    for table_name, table in tables.items():
        # Get the schema for the table.
        schema = get_schema_for_table(table)
        # Clear the data if delete_existing is True.
        if delete_existing:
            db[table_name].delete_many({})
        # Insert the data.
        db[table_name].insert_many(table["data"].to_dict("records"))


def get_schema_for_collection(db, collection_name: str) -> dict:
    """
    Get the JSON-schema for a collection.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        dict: The JSON-schema for the collection.

    Examples:
        >>> get_schema_for_collection("collections")
        {'$schema': 'http://json-schema.org/draft-07/schema#', 'type': 'object', 'properties': {'name': {'type': 'string'}}}
    """
    # Check if the collection exists.
    if collection_name not in db.list_collection_names():
        raise ValueError(f"Collection {collection_name} does not exist.")
    # Get the schema for the collection.
    schema_response = db["schemas"].find_one({"name": collection_name})
    if schema_response == None or "schema" not in schema_response:
        raise ValueError(f"Schema not found for [{collection_name}]")
    return schema_response["schema"]


def get_client_and_db() -> Tuple[MongoClient, Database]:
    """
    Get a MongoDB client and database.

    Returns:
        Tuple[pymongo.MongoClient, pymongo.database.Database]: A tuple containing the MongoDB client and database.

    Examples:
        >>> client, db = get_client_and_db()
    """
    mongo_port = os.environ.get("MONGO_PORT", 27020)
    mongo_host = os.environ.get("MONGO_HOST", "localhost")
    mongo_client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
    db = mongo_client["data"]
    return mongo_client, db


__all__ = ["ingest_from_xlsx", "get_schema_for_collection", "get_client_and_db"]
