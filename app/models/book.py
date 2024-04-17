from flask import jsonify, abort, request
from flask_restful import Resource
from datetime import datetime
from database import db
# from app import ma

class Book(db.Model):

  __tablename__ = 'books'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.String(255), nullable=False)
  auction_id = db.Column(db.String(255), nullable=False)
  bid_amount = db.Column(db.Integer)
  bitFirstAmount = db.Column(db.Integer)
  maxAmount = db.Column(db.Integer)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
  updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

# class BookSchema(ma.Schema):
#   class Meta:
#     # Fields to expose
#     fields = ("id", "auction_id", "created_at")

# book_schema = BookSchema(many=True)

# class Bookapi(Resource):
#   def get(self):
#     # １件取得
#     id = request.args.get('id')
#     result = Book.query.filter_by(id=id).all()
#     if len(result) != 0: 
#         return jsonify({"users" : book_schema.dump(result)})
#     else:
#         abort(404)

#   def post(self):
#     # 作成
#     print(request.json)
#     users = request.json["users"]
#     for i in users:
#         u  = User(name=i["name"])
#         db.session.add(u)
#     db.session.commit()

#     return '', 204

#   def put(self):
#     # 更新
#     id = request.json["id"]
#     user = Book.query.filter_by(id=id).first()
    
#     if user : 
#         for key, val in request.json.items():
#             setattr(user, key, val)
#         db.session.commit()
#     else:
#         abort(404)

#     return '', 204

#   def delete(self):
#     # 削除
#     id = request.args.get('id')
#     user = Book.query.filter_by(id=id).first()
#     if user :
#         db.session.delete(user)
#         db.session.commit()
#         return '', 204
#     else:
#       abort(404)