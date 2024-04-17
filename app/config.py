import os

class DevConfig:
  DEBUG = True

  # SQLAlchemy
  SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{dbname}?charset=utf8'.format(**{
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'the_booker_api-db-1'),
    # 'port': os.getenv('DB_PORT', 33306),
    'dbname': os.getenv('DB_NAME', 'booker')
  })
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = False

Config = DevConfig