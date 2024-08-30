import sys
from flask import Blueprint,redirect,send_file
# from app.controllers.auth_controller import test, check_link, authenticate
sys.path.append('../')
from controllers.auth_controller import *
from controllers.schedule_controller import *

routes_bp = Blueprint('routes', __name__)

@routes_bp.route("/api/test", methods=["GET"])
def test_route():
  return test()

@routes_bp.route('/api/check-link-ebay', methods=['GET'])
def check_link_route():
  return check_link()

@routes_bp.route('/api/authenticate', methods=['POST'])
def authenticate_route():
  return authenticate()

@routes_bp.route("/redirect", methods=["GET"])
def redirect_thebooker_route():
    data = request.get_data
    params = str(data).split('?')[-1].split("'")[0]
    print(params)
    return redirect(f'thebooker://(tab)/book?{params}')

@routes_bp.route('/schedule', methods=['GET'])
def schedule_route():
  return schedule_task()

@routes_bp.route("/api/check_prod", methods=["GET"])
def check_prod_route():
    id = request.args.get('id')
    print('id: ', id)
    from check_prod_scraping import hoge
    result = hoge(id)
    print('-task-', result)
    return result

@routes_bp.route("/api/get_img", methods=["GET"])
def get_img_route():
    try:
        id = request.args.get('auctionId')
        filename = f'images/{id}.png'
        print(filename)
        return send_file(filename, mimetype='image/jpeg')
    except Exception as e:
        print('画像なし')
        return jsonify({'status': ''}), 404