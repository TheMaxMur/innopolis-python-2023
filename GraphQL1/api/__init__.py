import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate


load_dotenv()


app = Flask(__name__)
migrate = Migrate()
CORS(app)

HOST_DB = os.getenv('HOST_DB')
PORT_DB = os.getenv('PORT_DB')
USER_DB = os.getenv('USER_DB')
NAME_DB = os.getenv('NAME_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')


app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()
db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def healthcheck():
    data = {
        "status": "ok",
        "code": 200
    }
    return data
