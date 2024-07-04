from flask import jsonify, abort, request
from flask_restful import Resource
from datetime import datetime
from database import db
import zoneinfo

class User(db.Model):

  __tablename__ = 'user'

  id = db.mapped_column(db.Integer, primary_key=True)
  uid = db.mapped_column(db.String(255), nullable=False)
  yahoo_id = db.mapped_column(db.String(255))
  yahoo_password = db.mapped_column(db.String(255))
  created_at = db.mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')))
  updated_at = db.mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')), onupdate=lambda: datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')))

  def to_dict(self):
    return {
      'id': self.id,
      'uid': self.uid if self.uid else None,
      'yahoo_id': self.yahoo_id if self.yahoo_id else None,
      'yahoo_password': self.yahoo_password if self.yahoo_password else None,
    }

class Userapi(Resource):
  def get(self):
    # userの取得
    uid = request.args.get('uid')
    print(uid)
    user = User.query.filter_by(uid=uid).first()

    return jsonify({'user': user.to_dict()})
    # abort(404)
