import json
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
  product_name = db.Column(db.String(255), nullable=False)
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

class Bookapi(Resource):
  def get(self):
    # １件取得
    user_id = request.args.get('user_id')
    print(user_id)
    result = Book.query.filter_by(user_id=user_id).all()

    print('---------', result)
    books = []
    for record in result:
    #   print(json.dump(book))
      books.append({
        'id': record.id,
        'auction_id': record.auction_id,
      })
    
    return jsonify({'books': books})

    # # return jsonify({"book" : book_schema.dump(result)})
    # return result

        # abort(404)

  def post(self):
    # 作成
    print('----post request.json----', request.json)
    book = request.json["book"]
    print('----book----', book)
    book_object = Book(user_id=1, auction_id=book["auction_id"])
    print('----book_object----', book_object)
    db.session.add(book_object)
    db.session.commit()

    return '', 204

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