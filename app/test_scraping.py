import os
import pytz
from flask import Flask, request
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from models.book import Bookapi, Book
from models.user import Userapi, User
from database import db
import time

def pop_up_click(el):
  try:
    el.click()
  except Exception as e:
    print(e)


# Yahooにログインして入札する
def hoge(auction_id, bid_first_amount, user_id):
  FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"images/{auction_id}.png")
  user = User.query.filter_by(uid=user_id).first()
  print('----user----', user)
  error_place = ''
  try:
    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
                command_executor = 'http://selenium:4444/wd/hub',
                options = options
                )
    driver.implicitly_wait(10)

    ########
    # yahooログイン
    ########
    url = 'https://login.yahoo.co.jp/config/login?auth_lv=pw&.lg=jp&.intl=jp&.src=auc&.done=https%3A%2F%2Fauctions.yahoo.co.jp%2Fuser%2Fjp%2Fshow%2Fmystatus&sr_required=birthday%20gender%20postcode%20deliver'
    print('-------driver get start-------')
    driver.get(url)
    time.sleep(1)
    print('-------driver get end-------')
    # id
    error_place = 'id入力'
    login_bar = driver.find_element(By.ID, "login_handle")
    login_bar.send_keys(user.yahoo_id)
    next_button = driver.find_element(By.XPATH, "//*[@id='content']/div[1]/div/form/div[1]/div[1]/div[2]/div/button")
    next_button.click()
    time.sleep(1)
    # パスワード
    error_place = 'パスワード入力'
    password_bar = driver.find_element(By.ID, "password")
    password_bar.send_keys(user.yahoo_password)
    login_button = driver.find_element(By.XPATH, "//*[@id='content']/div[1]/div/form/div[2]/div/div[1]/div[2]/div[3]/button")
    login_button.click()
    time.sleep(1)
    # 商品ページへ
    error_place = '商品ページ遷移'
    driver.get(f'https://page.auctions.yahoo.co.jp/jp/auction/{auction_id}')
    time.sleep(1)
    # ポップアップあったら消す
    error_place = 'ポップアップ消す'
    print('ポップアップ取得前')
    prMdl = driver.find_element(By.XPATH, "//*[@id='js-prMdl-close']")
    print('ポップアップあるか判定前', prMdl)
    pop_up_click(prMdl)
    print('ポップアップクリックした後')
    time.sleep(2)
    # 入札するボタン
    error_place = '入札ボタン押す'
    bid_button = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[1]/div[1]/div[2]/div[2]/div/div/a")
    bid_button.click()
    time.sleep(3)
    # 金額入力
    error_place = '金額入力'
    bid_amount_input = driver.find_element(By.XPATH, "//*[@id='BidModals']/div[2]/div[2]/div[2]/form/div[1]/label/input")
    bid_amount_input.clear()
    bid_amount_input.send_keys(bid_first_amount)
    time.sleep(2)
    # 確認ボタン
    error_place = '確認ボタン押す'
    confirm_button = driver.find_element(By.XPATH, "//*[@id='BidModals']/div[2]/div[2]/div[2]/form/div[3]/span/input")
    confirm_button.click()
    driver.save_screenshot(FILENAME)
    time.sleep(5)

    # 入札後のxpath（入札を受け付けました。あなたが現在の最高額入札者です。）
    # //*[@id="yaucBidAct"]/div[2]/div[1]/div[2]/div[2]/div[1]
    driver.quit()

    from app import app
    with app.app_context():  # app_context内で実行
      book = Book.query.filter_by(auction_id=auction_id).first()
      now = datetime.now(pytz.timezone('Asia/Tokyo'))
      noww = now.strftime('%Y-%m-%d %H:%M:%S')
      book.bid_time = noww
      if book:
        db.session.add(book)
        db.session.commit()
    return 'success'
  except Exception as e:
    print('hogeでエラー: ', e)
    time.sleep(3)
    driver.save_screenshot(FILENAME)
    driver.quit()
    from app import app
    with app.app_context():  # app_context内で実行
      book = Book.query.filter_by(auction_id=auction_id).first()
      now = datetime.now(pytz.timezone('Asia/Tokyo'))
      noww = now.strftime('%Y-%m-%d %H:%M:%S')
      book.bid_time = noww
      book.error = f'{error_place} の箇所で "{e}"'
      if book:
        db.session.add(book)
        db.session.commit()
    return 'failed'
