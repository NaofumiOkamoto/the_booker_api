import os
import base64
import requests
import time
from models.ebay import EbayToken
from flask import jsonify, request

def test():
    return jsonify({'test': 'OK'})

def check_link():
    try:
        uid = request.args.get('uid')
        print('----args.get(uid)-----', uid)
        ebay_token = EbayToken.query.filter_by(uid=uid).first()
        print('ebay_token record: ', ebay_token)
        if(ebay_token):
            return jsonify({'ebay_token': ebay_token.to_dict()})
    except Exception as e:
        print('エラー: ', e)
    return jsonify({'result': 'test'})

def authenticate():
    print('start authenticate')
    EBAY_ENV = os.getenv('EBAY_ENV')
    EBAY_AUTH_URL = os.getenv('EBAY_AUTH_URL_SAND_BOX') if EBAY_ENV!='production' else os.getenv('EBAY_AUTH_URL')
    redirect_uri = os.getenv('REDIRECT_URI_SAND_BOX') if EBAY_ENV!='production' else os.getenv('REDIRECT_URI')
    client_id = os.getenv('CLIENT_ID_SAND_BOX') if EBAY_ENV!='production' else os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET_SAND_BOX') if EBAY_ENV!='production' else os.getenv('CLIENT_SECRET')
    print('REDIRECT_URI', redirect_uri)
    print('CLIENT_ID', client_id)
    print('CLIENT_SECRET', client_secret)
    print('EBAY_AUTH_URL', EBAY_AUTH_URL)

    try:
        code = request.json.get('fullyDecodedStr')
        uid = request.json.get('uid')
        print('code: ', code)
        print('uid: ', uid)
        if not code:
            return jsonify({'error': 'No code provided'}), 400

        # eBayのアクセストークンを取得
        print('------get token-------')
        token_response = requests.post(EBAY_AUTH_URL, data={
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
            }, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()}'
        }
        )
        token_response.raise_for_status()
        ebay_access_token = token_response.json()['access_token']
        print('token_response: ', token_response)
        print('token_response.access_token: ', ebay_access_token)

        time.sleep(3)
        # eBayのユーザー情報を取得
        print('------get ebay user-------')
        url = 'https://apiz.ebay.com/commerce/identity/v1/user' if EBAY_ENV=='production' else 'https://apiz.sandbox.ebay.com/commerce/identity/v1/user'
        user_response = requests.get(url, headers={
            'Authorization': f'Bearer {ebay_access_token}'
        })
        user_response.raise_for_status()
        user_response_userId = user_response.json()['userId']
        print('user_response: ', user_response)
        print('user_response_userId: ', user_response_userId)
        ebay_user = user_response.json()
        user_id = ebay_user['userId']
        user_name = ebay_user['username']

        # DBにEbayTokenレコード作成
        if uid:
            create_token = dict(**token_response.json(), **{'user_id': user_id}, **{'user_name': user_name}, **{'uid': uid})
            print('create_token: ', create_token)
            EbayToken.create_token(create_token)

        return jsonify({'ebay_user': ebay_user})

    except requests.RequestException as e:
        return jsonify({'error': 'Authentication failed', 'details': str(e)}), 400
