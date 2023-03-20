"""
This is a base implementation of a metadata API for the BossDB BICCN project.

The API supports all endpoints for the BICCN specification, and is self-
documenting using the Flask framework. The database is a MongoDB instance
running in a config-specified location (which we anticipate will run in a
parallel docker-compose container). The API itself does not contain any schema
information at all; the schema is defined in the database, and the API simply
exposes the database's functionality and queries.

The data are uploaded to the database using the `upload_from_xlsx` function,
where each sheet in the Excel file is a collection in the database. The
`upload_from_xlsx` function is not part of the API, and is only used for
administrative purposes during initialization.

All functions and entities in this file are documented using Google-style
docstrings, and unittests are provided for all functions in the doctest
format. The doctests can be run with pytest.

## General Requirements
- [x] If the API requires authentication, an individual user can authenticate
      themselves with an API Key or OAuth access token to interact with the API
- [x] A downstream service can authenticate with an API Key to automate
      interactions with the API.
- [x] Consistent, persistent identifiers
- [x] Object schema documentation
- [x] Versioned data schemas
- [ ] Related objects are linked
- [x] Consistent response status codes
- [x] Endpoint docs
- [x] Filtering results
- [ ] Filter on BCDC id
- [x] Search by each column

"""
from flask import Flask
import json

from .endpoints import (
    get_endpoint,
    get_endpoint_document_by_id,
    get_endpoint_document_by_query,
    get_endpoint_schema,
    api_root,
    home,
)

from .db import ingest_from_xlsx, get_client_and_db

app = Flask(__name__)
app.url_map.strict_slashes = False

mongo_client, db = get_client_and_db()

# API Root
app.add_url_rule("/api/v1/", "api-root", api_root, methods=["GET"])
app.add_url_rule("/", "ui-home", home, methods=["GET"])

# Collection Endpoints
for endpoint_name, collection_name, type_name in [
    ("ramonsynapse", "ramonsynapse", "RAMONSynapse"),
    ("ramonsegment", "ramonsegment", "RAMONSegment"),
    ("ramonsubcellular", "ramonsubcellular", "RAMONSubcellular"),
    ("ramonroi", "ramonroi", "RAMONroi"),
    ("ramonneuron", "ramonneuron", "RAMONNeuron"),
]:
    # Get a list of all of the documents in the collection.
    app.add_url_rule(
        f"/api/v1/{endpoint_name}",
        endpoint_name,
        get_endpoint(db, endpoint_name, collection_name),
        methods=["GET"],
    )

    # Get a single document from the collection by its ID.
    app.add_url_rule(
        f"/api/v1/{endpoint_name}/id/<id>",
        f"{endpoint_name}-id",
        get_endpoint_document_by_id(db, endpoint_name, collection_name),
        methods=["GET"],
    )

    # Get a single document from the collection by request body query.
    app.add_url_rule(
        f"/api/v1/{endpoint_name}/query",
        f"{endpoint_name}-query",
        get_endpoint_document_by_query(db, endpoint_name, collection_name),
        methods=["POST"],
    )

    app.add_url_rule(
        f"/api/v1/{endpoint_name}/schema",
        f"{endpoint_name}-schema",
        get_endpoint_schema(db, endpoint_name, collection_name, type_name),
        methods=["GET"],
    )

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

ingest_from_xlsx(db, "ramondata.xlsx", delete_existing=True)
