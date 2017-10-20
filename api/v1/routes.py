from flask import Flask, jsonify, abort, request 
import json
from . import *
import vk
import api.common as common
import requests

VK_INCORRECT_TOKEN_ID = 15


items = [
    {
        'id': 1,
        'title': u'First item'
    },
    {
        'id': 2,
        'title': u'Second item'
    }
]

def get_vk_server_token(client_id, client_secret):
    # Request (3)
    # GET https://oauth.vk.com/access_token

    response = requests.get(
        url="https://oauth.vk.com/access_token",
        params={
            "client_id": client_id,
            "client_secret": client_secret,
            "v": "5.68",
            "grant_type": "client_credentials",
        }

    result = json.loads(response.content)["access_token"]
    return result

def vk_get_user(vk_token, user_id):
    session = vk.Session(access_token=vk_token)
    vk_api = vk.API(session)
    return vk_api.users.get()

def auth_user(vk_token, user_id, user_dict):
    result_dict = user_dict
    result_dict['vk_token'] = vk_token
    result_dict['id'] = user_id
    del result_dict['uid']

    client = common.get_db()

    db_user = client.get_user(user_id)
    if db_user is None:
        db_user = client.create_user(result_dict)

    del db_user['_id']
    del db_user['vk_token']
    
    return db_user
    

@api.route('/items', methods=['GET'])
def get_tasks():
    return jsonify({'items': items})

@api.route('/auth', methods=['POST'])
def get_vk_users():
    data = request.data
    data_dict = json.loads(data)

    token = data_dict['token']

    vk_server_token = get_vk_server_token(client_id=common.VK_CLIENT_ID, client_secret=common.VK_CLIENT_SECRET)
    session = vk.Session(access_token=vk_server_token)
    vk_api = vk.API(session)
    
    try:
        result = vk_api.secure.checkToken(token=token, client_secret=common.VK_CLIENT_SECRET)

        user_token = token
        user_id = result['user_id']
        user_data = vk_get_user(user_token, user_id)

        if user_data:
            user_dict = user_data[0]
            result_user = auth_user(user_token, user_id, user_dict)
            print result_user
            result = result_user

    except vk.exceptions.VkAPIError as e:
        result = {'vk_error_code': e.code}
        error_code = 400
        if e.code == VK_INCORRECT_TOKEN_ID:
            error_code = 401
            print 'Incorrect token'
        return jsonify(result), error_code

    return jsonify(result)