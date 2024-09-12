import json
from flask import jsonify, abort, request
from flask_restful import Resource
from email.utils import parsedate_to_datetime
from datetime import datetime
from database import db, init_db
import zoneinfo
# from app import ma

class Book(db.Model):

  __tablename__ = 'books'

  id = db.mapped_column(db.Integer, primary_key=True)
  user_id = db.mapped_column(db.String(255), nullable=False)
  item_number = db.mapped_column(db.String(255), nullable=False)
  product_name = db.mapped_column(db.String(255), nullable=False)
  current_price = db.mapped_column(db.Float)
  bid_amount = db.mapped_column(db.Float)
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
#     fields = ("id", "item_number", "created_at")

# book_schema = BookSchema(many=True)
  def to_dict(self):
      return {
          'id': self.id,
          'item_number': self.item_number if self.item_number else None,
          'product_name': self.product_name if self.product_name else None,
          'current_price': self.current_price if self.current_price else None,
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
    user_id = request.args.get('uid')
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
        'item_number': record.item_number,
        'current_price': record.current_price,
        'product_name': record.product_name,
        'bid_amount': record.bid_amount,
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
      date_obj = datetime.strptime(book["end_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
      book_object = Book(
        user_id=book["user_id"],
        item_number=book["item_number"],
        product_name=book["title"],
        current_price=book["current_price"],
        bid_amount=book["bid_amount"],
        close_time=date_obj.strftime("%Y-%m-%d %H:%M:%S"),
        seconds=book["seconds"],
      )
      print('----book_object----', book_object)
      db.session.add(book_object)
      db.session.commit()
      return '', 204
    except Exception as e:
      print('予約作成エラ〜', e)
