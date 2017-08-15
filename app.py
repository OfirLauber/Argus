import json
from json import JSONDecodeError

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient

import config
from exceptions import *

app = Flask(__name__)
CORS(app)
client = MongoClient(config.MONGO_HOST, config.MONGO_PORT)


@app.route('/swagger')
def swagger():
    with open('./swagger.json') as swagger_file:
        return Response(swagger_file.read(), mimetype='application/json')


@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path):
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
        except JSONDecodeError:
            return "Not a JSON", 400

        _insert_data(path, data)
        return "OK"
    else:
        try:
            return jsonify(_get_data(path))
        except ItemNotFoundError:
            return 'Item not found!', 404


def _insert_data(path, data):
    paths_collection = client[config.DB_NAME][config.PATHS_COLLECTION_NAME]

    query = {"_id": path}

    document = {
        "_id": path,
        "data": data
    }

    paths_collection.replace_one(query, document, upsert=True)


def _get_data(path):
    query = {"_id": path}
    paths_collection = client[config.DB_NAME][config.PATHS_COLLECTION_NAME]

    result = paths_collection.find_one(query)

    if result:
        return result['data']
    else:
        raise ItemNotFoundError


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.APP_PORT, threaded=True)
