import datetime
from celery_utils import make_celery
from flask import Flask,request,jsonify,send_file,redirect
from database import init_db
from flask_restful import Api
from flask_marshmallow import Marshmallow
from models.book import Book, Bookapi
from models.user import User, Userapi
from test_scraping import hoge
from flask_cors import CORS
from routes.routes import routes_bp

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'
celery = make_celery(app)
ma = Marshmallow(app)
api = Api(app)
init_db(app)
CORS(app)

api.add_resource(Bookapi, '/api/book', '/api/book/<int:id>')
api.add_resource(Userapi, '/api/user')
app.register_blueprint(routes_bp)

##server run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)