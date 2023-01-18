import datetime
import simplejson as json
from bson import ObjectId
from flask import request, jsonify, render_template, current_app
from bson import json_util

from .db import get_schema_for_collection


def home():
    """
    Get the home page.

    Returns:
        flask.Response: A Flask response object containing the home page.

    """
    return render_template("home.html")


def api_root():
    """
    Get the API root.

    Returns:
        flask.Response: A Flask response object containing the API root.

    """
    routes = {}
    for rule in current_app.url_map.iter_rules():
        routes[rule.endpoint] = {
            "methods": list(rule.methods),
            "endpoint": rule.rule,
            "arguments": list(rule.arguments),
        }
    return jsonify(
        {
            "data": {
                "type": "api-root",
                "id": "api-root",
                "attributes": {
                    "name": "BICCN Metadata API",
                    "description": "This is a base implementation of a metadata API for the BossDB BICCN project.",
                    "version": "0.1.0",
                    "endpoints": routes,
                },
            },
            "server_time": datetime.datetime.now().isoformat(),
        }
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


def get_endpoint(db, endpoint_name, collection_name):
    def get_endpoint_func():
        query_result = list(db[collection_name].find())
        query_count = len(query_result)
        return jsonify(
            {
                "data": [
                    {
                        "type": endpoint_name,
                        "id": str(document["_id"]),
                        "attributes": {
                            **json_compat_wrap(document),
                        },
                    }
                    for document in query_result
                ],
                "count": query_count,
                "schema": json_compat_wrap(
                    get_schema_for_collection(db, collection_name)
                ),
                "endpoints": {
                    "self": f"/api/v1/{endpoint_name}/",
                    "schema": f"/api/v1/{endpoint_name}/schema",
                    "query": f"/api/v1/{endpoint_name}/query",
                    "document": f"/api/v1/{endpoint_name}/<id>",
                },
                "server_time": datetime.datetime.now().isoformat(),
            }
        )

    return get_endpoint_func


def get_endpoint_document_by_id(db, endpoint_name, collection_name):
    def get_endpoint_document_by_id_func(id):
        query_result = db[collection_name].find_one({"_id": ObjectId(id)})
        if query_result == None:
            return jsonify(
                {
                    "data": None,
                    "count": 0,
                    "schema": json_compat_wrap(
                        get_schema_for_collection(db, collection_name)
                    ),
                    "endpoints": {
                        "list": f"/api/v1/{endpoint_name}/",
                        "schema": f"/api/v1/{endpoint_name}/schema",
                        "query": f"/api/v1/{endpoint_name}/query",
                        "self": f"/api/v1/{endpoint_name}/<id>",
                    },
                    "server_time": datetime.datetime.now().isoformat(),
                }
            )
        return jsonify(
            {
                "data": {
                    "type": endpoint_name,
                    "id": str(query_result["_id"]),
                    "attributes": {
                        **json_compat_wrap(query_result),
                    },
                },
                "count": 1,
                "schema": json_compat_wrap(
                    get_schema_for_collection(db, collection_name)
                ),
                "endpoints": {
                    "list": f"/api/v1/{endpoint_name}/",
                    "schema": f"/api/v1/{endpoint_name}/schema",
                    "query": f"/api/v1/{endpoint_name}/query",
                    "self": f"/api/v1/{endpoint_name}/<id>",
                },
                "server_time": datetime.datetime.now().isoformat(),
            }
        )

    return get_endpoint_document_by_id_func


def get_endpoint_document_by_query(db, endpoint_name, collection_name):
    def get_endpoint_document_by_query_func():
        # Get the query parameters from the body of the request.
        try:
            query = request.get_json() or {}
        except:
            return jsonify(
                {
                    "error": "Could not parse query from request body.",
                    "server_time": datetime.datetime.now().isoformat(),
                },
                400,
            )

        # In the short-term, we are going to assume that the query is a simple
        # dictionary of key-value pairs. In the long-term, we will want to
        # support more complex queries, but this enables us to get started in
        # the short-term without having to worry about the end user maliciously
        # introducing a query with averse effects.
        schema = get_schema_for_collection(db, collection_name)
        sanitized_query = {}
        # Loop through the query and make sure that the keys are valid entries
        # in the schema.
        for key in query:
            if key not in schema["properties"]:
                return jsonify(
                    {
                        "error": f"Invalid query key: {key}",
                        "endpoints": {
                            "list": f"/api/v1/{endpoint_name}",
                            "self": f"/api/v1/{endpoint_name}/query",
                            "schema": f"/api/v1/{endpoint_name}/schema",
                            "document": f"/api/v1/{endpoint_name}/<id>",
                        },
                        "server_time": datetime.datetime.now().isoformat(),
                    },
                    400,
                )
            sanitized_query[key] = query[key]

        # Execute the query.
        query_result = list(db[collection_name].find(sanitized_query))
        query_count = len(query_result)
        return jsonify(
            {
                "data": [
                    {
                        "type": endpoint_name,
                        "id": str(document["_id"]),
                        "attributes": {
                            **json_compat_wrap(document),
                        },
                    }
                    for document in query_result
                ],
                "count": query_count,
                "schema": json_compat_wrap(schema),
                "endpoints": {
                    "self": f"/api/v1/{endpoint_name}",
                    "query": f"/api/v1/{endpoint_name}/query",
                    "schema": f"/api/v1/{endpoint_name}/schema",
                    "document": f"/api/v1/{endpoint_name}/<id>",
                },
                "server_time": datetime.datetime.now().isoformat(),
            }
        )

    return get_endpoint_document_by_query_func


def get_endpoint_schema(db, endpoint_name, collection_name, type_name):
    def get_endpoint_schema_func():
        return jsonify(
            {
                "data": {
                    "type": "schema",
                    "id": f"{endpoint_name}-schema",
                    "endpoints": {
                        "self": f"/api/v1/{endpoint_name}/schema",
                        "list": f"/api/v1/{endpoint_name}/",
                        "query": f"/api/v1/{endpoint_name}/query",
                        "document": f"/api/v1/{endpoint_name}/<id>",
                    },
                    "schema": json_compat_wrap(
                        get_schema_for_collection(db, collection_name)
                    ),
                    "attributes": {
                        "data": {
                            "type": f"[{type_name}]",
                            "description": f"A list of {collection_name}.",
                        },
                        "count": {
                            "type": "int",
                            "description": f"The number of {collection_name} returned by this request.",
                        },
                        "schema": {
                            "type": "dict",
                            "description": f"The JSON-schema for the {collection_name} collection.",
                        },
                        "server_time": {
                            "type": "string",
                            "description": "The ISO time at which the response was generated.",
                        },
                    },
                },
                "server_time": datetime.datetime.now().isoformat(),
            }
        )

    return get_endpoint_schema_func


__all__ = [
    "get_endpoint_document_by_id",
    "get_endpoint_document_by_query",
    "get_endpoint_schema",
    "api_root",
    # Templates:
    "home",
]
