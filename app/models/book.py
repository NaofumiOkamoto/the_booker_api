import json
from flask import jsonify, abort, request
from flask_restful import Resource
from datetime import datetime
from database import db, init_db
import zoneinfo
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
  is_processed = db.mapped_column(db.Boolean)
  task_id = db.mapped_column(db.String(255))
  bid_time = db.mapped_column(db.DateTime)
  is_succeeded = db.mapped_column(db.Boolean)
  error = db.mapped_column(db.Text)
  close_time = db.mapped_column(db.DateTime)
  created_at = db.mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')))
  updated_at = db.mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')), onupdate=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')))

# class BookSchema(ma.Schema):
#   class Meta:
#     # Fields to expose
#     fields = ("id", "auction_id", "created_at")

# book_schema = BookSchema(many=True)
  def to_dict(self):
      return {
          'id': self.id,
          'auction_id': self.auction_id if self.auction_id else None,
          'product_name': self.product_name if self.product_name else None,
          'bid_first_amount': self.bid_first_amount if self.bid_first_amount else None,
          'max_amount': self.max_amount if self.max_amount else None,
          'seconds': self.seconds if self.seconds else None,
          'is_processed': self.is_processed if self.is_processed else None,
          'bid_time': self.bid_time if self.bid_time else None,
          'is_succeeded': self.is_succeeded if self.is_succeeded else None,
          'error': self.error if self.error else None,
          'close_time': self.close_time.strftime('%Y-%m-%d %H:%M:%S') if self.close_time else None,
          # 他のフィールドを辞書に追加
      }

class Bookapi(Resource):
  def get(self):
    # userの取得
    user_id = request.args.get('user_id')
    print(user_id)
    result = Book.query.filter_by(user_id=user_id).order_by(Book.created_at.desc()).all()

    books = []
    for record in result:
      jst_created_dt = record.created_at.strftime('%Y/%m/%d %H:%M:%S')
      jst_close_time = record.close_time.strftime('%Y/%m/%d %H:%M:%S')
      jst_bid_time = None
      bid_time = record.bid_time
      if bid_time:
        jst_bid_time = bid_time.strftime('%Y/%m/%d %H:%M:%S')

      books.append({
        'id': record.id,
        'platform_name': record.platform_name,
        'auction_id': record.auction_id,
        'product_name': record.product_name,
        'bid_first_amount': record.bid_first_amount,
        'max_amount': record.max_amount,
        'seconds': record.seconds,
        'bid_time': jst_bid_time,
        'close_time': jst_close_time,
        'created_at': jst_created_dt,
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
        user_id=book["user_id"],
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
