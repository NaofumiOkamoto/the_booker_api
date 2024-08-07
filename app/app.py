import datetime
import time
import pytz
import re
import requests
import os
import jwt
import base64
from celery_utils import make_celery
from flask import Flask,request,jsonify,send_file,redirect
from database import init_db
from flask_restful import Api
from flask_marshmallow import Marshmallow
from models.book import Book, Bookapi
from models.user import User, Userapi
from models.ebay import EbayToken
from test_scraping import hoge
from database import db

from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'
celery = make_celery(app)
ma = Marshmallow(app)
api = Api(app)
init_db(app)
# EBAY_AUTH_URL = 'https://api.ebay.com/identity/v1/oauth2/token'
EBAY_AUTH_URL_SAND_BOX = 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
JWT_SECRET = 'test'

@celery.task(name="app.run_test")
def run_test(auction_id, bid_first_amount, user_id):
    with app.app_context():
        print('run_test auction_id: ', auction_id)
        from test_scraping import hoge
        result = hoge(auction_id, bid_first_amount, user_id)
        return f"Task completed at {datetime.datetime.now().isoformat()} - Result: {result}"

@app.route('/schedule', methods=['GET'])
def schedule_task():
    # book = Book.query.get(42)
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    now_jst_5 = now_jst + datetime.timedelta(minutes=5)
    print('now_jst', now_jst)
    print('now_jst_5', now_jst_5)
    datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    books = Book.query.filter(
        Book.close_time > now_jst,
        Book.close_time < now_jst_5,
        Book.task_id == None,
        Book.bid_time == None
    ).all()

    if not books:
        return jsonify({"error": "Book not found"}), 404

    tasks = []
    for book in books:
        print(book.to_dict())
        close_time = book.close_time

        if close_time.tzinfo is None:
            close_time = jst.localize(close_time)
        else:
            close_time = close_time.astimezone(jst)
        
        delay = (close_time - now_jst).total_seconds()
        print(close_time)
        print(now_jst)
        print(delay)
        if delay < 0:
            return jsonify({"error": "close_time is in the past"}), 400
        
        print(f'-----start run_test.apply_async--{book.auction_id}------')
        task = run_test.apply_async(args=[book.auction_id, book.bid_first_amount, book.user_id], countdown=delay) 
        print('-----end run_test.apply_async--------')
        tasks.append(task.id)
        book.task_id = task.id
        db.session.add(book)
        db.session.commit()
        print(task.id)

    return jsonify({'tasks': tasks, 'books': [book.to_dict() for book in books]}), 202

@app.route("/api/check_prod", methods=["GET"])
def index():
    id = request.args.get('id')
    print('id: ', id)
    from check_prod_scraping import hoge
    result = hoge(id)
    print('-task-', result)
    return result


@app.route("/api/get_img", methods=["GET"])
def get_img():
    try:
        id = request.args.get('auctionId')
        filename = f'images/{id}.png'
        print(filename)
        return send_file(filename, mimetype='image/jpeg')

    except Exception as e:
        print('画像なし')
        return jsonify({'status': ''}), 404

@app.route("/redirect", methods=["GET"])
def redirect_thebooker():
    data = request.get_data
    params = str(data).split('?')[-1].split("'")[0]
    print(params)
    return redirect(f'thebooker://(tab)/book?{params}')

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    print('start authenticate')
    print('REDIRECT_URI', os.getenv('REDIRECT_URI'))
    print('CLIENT_ID', os.getenv('CLIENT_ID'))
    print('CLIENT_SECRET', os.getenv('CLIENT_SECRET'))
    print('REDIRECT_URI_SAND_BOX', os.getenv('REDIRECT_URI_SAND_BOX'))
    print('CLIENT_ID_SAND_BOX', os.getenv('CLIENT_ID_SAND_BOX'))
    print('CLIENT_SECRET_SAND_BOX', os.getenv('CLIENT_SECRET_SAND_BOX'))
    code = request.json.get('fullyDecodedStr')
    print('code', code)
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        # eBayのアクセストークンを取得
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {base64.b64encode(f"{os.getenv('CLIENT_ID_SAND_BOX')}:{os.getenv('CLIENT_SECRET_SAND_BOX')}".encode()).decode()}'
        }
        token_response = requests.post(EBAY_AUTH_URL_SAND_BOX, data={
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': os.getenv('REDIRECT_URI_SAND_BOX'),
        }, headers=headers
        )
        print('token_response: ', token_response)
        print('token_response.json(): ', token_response.json())
        token_response.raise_for_status()
        ebay_access_token = token_response.json()['access_token']
        print('ebay_access_token: ', ebay_access_token)
        EbayToken.create_token(token_response.json())

        # eBayのユーザー情報を取得
        user_response = requests.get('https://apiz.sandbox.ebay.com/commerce/identity/v1/user', headers={
            'Authorization': f'Bearer {ebay_access_token}'
        })
        user_response.raise_for_status()
        print('user_response: ', user_response)
        ebay_user = user_response.json()
        # ebay_user_id = ebay_user['userId']
        print('ebay_user: ', ebay_user)

        # Bookerアプリのユーザーを見つけるか作成
        # booker_user = find_or_create_user(ebay_user_id, ebay_user)

        # JWTトークンを発行
        token = jwt.encode({
            # 'id': booker_user['id'],
            # 'name': booker_user['name'],
            'id': 1,
            'name': 'okamoto',
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }, JWT_SECRET, algorithm='HS256')
        print('token: ', token)

        return jsonify({'token': token, 'ebay_user': ebay_user})

    except requests.RequestException as e:
        return jsonify({'error': 'Authentication failed', 'details': str(e)}), 400

api.add_resource(Bookapi, '/book')
api.add_resource(Userapi, '/user')

##server run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)