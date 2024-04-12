# 簡単なindexページの作成を行っています。
from flask import Flask # type: ignore

app = Flask(__name__)

@app.route("/")
def index():
    return "index page"