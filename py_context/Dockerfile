# ベースイメージとしてpython公式
FROM python:latest
# Linux環境を整えるパッケージインストール
RUN apt-get update && \
    # お好みで必要なパッケージを追加してください
    apt-get install -y \
    build-essential \
    cmake \
    git \
    sudo \
    wget \
    vim \
    python3-pymysql
# pipの更新
RUN pip install --upgrade pip
# python libraryのリストをホストから取得
COPY ./requirements.txt /requirements.txt
# requirements.txt内のライブラリーを一括インストール
RUN pip install -r /requirements.txt
RUN pip3 install PyMySQL
WORKDIR /app
CMD ["/bin/bash"] 