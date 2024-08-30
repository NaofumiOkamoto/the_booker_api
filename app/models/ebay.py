from flask import jsonify, abort, request
from flask_restful import Resource
from datetime import datetime
from database import db
import zoneinfo

class EbayToken(db.Model):

  __tablename__ = 'ebay_token'

  id = db.mapped_column(db.Integer, primary_key=True)
  uid = db.mapped_column(db.String(255), nullable=False)
  user_id = db.mapped_column(db.String(255), nullable=False)
  user_name = db.mapped_column(db.String(255))
  access_token = db.mapped_column(db.Text)
  expires_in = db.mapped_column(db.Integer)
  refresh_token = db.mapped_column(db.Text)
  refresh_token_expires_in = db.mapped_column(db.Integer)
  token_type = db.mapped_column(db.String(255))
  created_at = db.mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')))
  updated_at = db.mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')), onupdate=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')))

  def to_dict(self):
    return {
      'id': self.id,
      'uid': self.uid,
      'user_id': self.user_id if self.user_id else None,
      'user_name': self.user_name if self.user_name else None,
      'access_token': self.access_token if self.access_token else None,
      'expires_in': self.expires_in if self.expires_in else None,
      'refresh_token': self.refresh_token if self.refresh_token else None,
      'refresh_token_expires_in': self.refresh_token_expires_in if self.refresh_token_expires_in else None,
      'token_type': self.token_type if self.token_type else None,
    }

  @staticmethod
  def create_token(data):
      try:
          token_object = EbayToken(
              user_id=data["user_id"],
              user_name=data["user_name"],
              access_token=data["access_token"],
              expires_in=data["expires_in"],
              refresh_token=data["refresh_token"],
              refresh_token_expires_in=data["refresh_token_expires_in"],
              token_type=data["token_type"],
              uid=data["uid"]
          )
          db.session.add(token_object)
          db.session.commit()
          return token_object
      except Exception as e:
          print('Error creating token:', e)
          db.session.rollback()
          return None

class Tokenapi(Resource):
  def get(self):
    uid = request.args.get('user_id')
    print(uid)
    token = EbayToken.query.filter_by(uid=uid).first()

    return jsonify({'user': token.to_dict()})

  def post(self):
    # 作成
    try:

      print('----post request.json----', request.json)
      token = request.json["token"]
      print('----token----', token)
      token_object = EbayToken(
        user_id=token["user_id"],
        platform_name=token["token"],
      )
      print('----book_object----', token_object)
      db.session.add(token_object)
      db.session.commit()
      return '', 204
    except Exception as e:
      print('予約作成エラ〜', e)