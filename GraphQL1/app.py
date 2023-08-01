from api import app, db
from api import models
from ariadne import (load_schema_from_path, make_executable_schema, 
                     graphql_sync, snake_case_fallback_resolvers, ObjectType)
from ariadne.constants import HTTP_STATUS_200_OK
from flask import request, jsonify
from api.queries import listPhones_revolver, getPhone_resolver
from api.mutations import createPhone_resolver, deletePhone_resolver, updatePhone_resolver


query = ObjectType("Query")
query.set_field("listPhones", resolver=listPhones_revolver)
query.set_field("getPhone", resolver=getPhone_resolver)


mutation = ObjectType("Mutation")
mutation.set_field("createPhone", resolver=createPhone_resolver)
mutation.set_field("deletePhone", resolver=deletePhone_resolver)
mutation.set_field("updatePhone", resolver=updatePhone_resolver)


type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return HTTP_STATUS_200_OK, 200
    

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code
