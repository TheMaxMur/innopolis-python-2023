from flask import Flask, jsonify, request
from extensions import bcrypt, auth, jwt
from schema import schema
from models import session, Users, Wishlists
from flask_jwt_extended import (
    create_access_token,
    # jwt_unauthorized_handler,
    create_refresh_token,
    get_jwt_identity,
    jwt_required, verify_jwt_in_request
)
from flask_graphql import GraphQLView


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string', 'json']
app.config['JWT_SECRET_KEY'] = 'jwt_secret'


app.add_url_rule(
	'/graphql', 
	view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


bcrypt.init_app(app)
auth.init_app(app)
jwt.init_app(app)


@app.route('/')
def healthcheck():
    data = {
        "status": "ok",
        "code": 200
    }
    return data


# @jwt_unauthorized_handler
def unauthorized_handler(err_str):
    return jsonify({"Error": "Missing or invalid access token"}), 401


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email = data.get('email')
    password = data.get('password')

    user = session.query(Users).filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify(message="Incorrect email address or password"), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200


@app.route("/authgraphql", methods=['POST'])
@jwt_required()
def auth_graphql():
    data = {"status": "ok"}
    return jsonify(data)


@app.route("/notauthgraphql", methods=['POST'])
def not_auth_graphql():
    auth_token = request.json.get("access_token")
    if auth_token:
        return jsonify({"status": "error"})

    return jsonify({"status": "ok"})
