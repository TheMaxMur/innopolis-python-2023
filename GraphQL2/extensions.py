from flask_bcrypt import Bcrypt
from flask_graphql_auth import GraphQLAuth
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
auth = GraphQLAuth()
jwt = JWTManager()
