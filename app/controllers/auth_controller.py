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
    # EBAY_AUTH_URL = 'https://api.ebay.com/identity/v1/oauth2/token'
    EBAY_AUTH_URL_SAND_BOX = 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
    print('start authenticate')
    print('REDIRECT_URI', os.getenv('REDIRECT_URI'))
    print('CLIENT_ID', os.getenv('CLIENT_ID'))
    print('CLIENT_SECRET', os.getenv('CLIENT_SECRET'))
    print('REDIRECT_URI_SAND_BOX', os.getenv('REDIRECT_URI_SAND_BOX'))
    print('CLIENT_ID_SAND_BOX', os.getenv('CLIENT_ID_SAND_BOX'))
    print('CLIENT_SECRET_SAND_BOX', os.getenv('CLIENT_SECRET_SAND_BOX'))

    try:
        code = request.json.get('fullyDecodedStr')
        uid = request.json.get('uid')
        print('code: ', code)
        print('uid: ', uid)
        if not code:
            return jsonify({'error': 'No code provided'}), 400

        # eBayのアクセストークンを取得
        print('------get token-------')
        token_response = requests.post(EBAY_AUTH_URL_SAND_BOX, data={
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': os.getenv('REDIRECT_URI_SAND_BOX'),
            }, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {base64.b64encode(f"{os.getenv('CLIENT_ID_SAND_BOX')}:{os.getenv('CLIENT_SECRET_SAND_BOX')}".encode()).decode()}'
        }
        )
        token_response.raise_for_status()
        ebay_access_token = token_response.json()['access_token']
        print('token_response: ', token_response)
        print('token_response.access_token: ', ebay_access_token)

        time.sleep(3)
        # eBayのユーザー情報を取得
        print('------get ebay user-------')
        user_response = requests.get('https://apiz.sandbox.ebay.com/commerce/identity/v1/user', headers={
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
