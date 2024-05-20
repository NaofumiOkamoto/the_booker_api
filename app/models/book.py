import json
from flask import jsonify, abort, request
from flask_restful import Resource
from datetime import datetime
from database import db
# from app import ma

class Book(db.Model):

  __tablename__ = 'books'

  id = db.mapped_column(db.Integer, primary_key=True)
  user_id = db.mapped_column(db.String(255), nullable=False)
  platform_name = db.mapped_column(db.String(255), nullable=False)
  auction_id = db.mapped_column(db.String(255), nullable=False)
  product_name = db.mapped_column(db.String(255), nullable=False)
  bid_amount = db.mapped_column(db.Integer)
  bid_first_amount = db.mapped_column(db.Integer)
  max_amount = db.mapped_column(db.Integer)
  seconds = db.mapped_column(db.Integer)
  close_time = db.mapped_column(db.DateTime)
  created_at = db.mapped_column(db.DateTime, nullable=False, default=datetime.now)
  updated_at = db.mapped_column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

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

    books = []
    for record in result:
      books.append({
        'id': record.id,
        'platform_name': record.platform_name,
        'auction_id': record.auction_id,
        'product_name': record.product_name,
        'bid_first_amount': record.bid_first_amount,
        'max_amount': record.max_amount,
        'seconds': record.seconds,
        'close_time': record.close_time
      })
    
    return jsonify({'books': books})

    # abort(404)

  def post(self):
    # 作成
    try:

      print('----post request.json----', request.json)
      book = request.json["book"]
      print('----book----', book)
      book_object = Book(
        user_id=1,
        platform_name=book["platform_name"],
        auction_id=book["auction_id"],
        product_name=book["product_name"],
        bid_first_amount=book["bid_first_amount"],
        max_amount=book["max_amount"],
        close_time=book["close_time"],
        seconds=book["seconds"],
      )
      print('----book_object----', book_object)
      db.session.add(book_object)
      db.session.commit()
      return '', 204
    except Exception as e:
      print('予約作成エラ〜', e)


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