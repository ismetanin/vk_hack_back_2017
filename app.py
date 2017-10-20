from flask import Flask, jsonify, g, current_app
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from api.v1 import api as api_v1

from api.db import MongoDBClient

__all__ = ['make_json_app']

def make_db_connect():
    db_client = MongoDBClient()
    return db_client

def make_json_app(import_name, **kwargs):
    """
    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

app = make_json_app('vk_hack_back')

app.register_blueprint(api_v1, url_prefix='/v1')

with app.app_context():
    # within this block, current_app points to app.
    print current_app.name
    current_app._database = make_db_connect()

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')