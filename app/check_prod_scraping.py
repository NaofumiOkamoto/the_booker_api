import os
import re
import pytz
from flask import Flask, jsonify
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from models.book import Bookapi, Book
from database import db
import time

# Yahooにログインして入札する
def hoge(id):
    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
                command_executor = 'http://the_booker_api-selenium-1:4444/wd/hub',
                options = options
                )

    url = f'https://page.auctions.yahoo.co.jp/jp/auction/{id}'
    print('-------driver get start-------')
    print(url)
    try:
        driver.get(url)
        product_title = driver.find_element(By.XPATH, "//*[@id='ProductTitle']/div/h1").text
        print('商品名: ', product_title)
        current_price = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[1]/div[1]/div[2]/dl/div[1]/dd").text
        print('現在価格: ', current_price)

        # 詳細ボタンを押して残り時間の詳細を取得する
        detail_button = driver.find_element(By.XPATH, '//*[@id="l-sub"]/div[2]/ul/li[1]/div[1]/div[2]/div[1]/ul[1]/li[2]/a')
        detail_button.click()
        time.sleep(1.7)
        driver.switch_to.window(driver.window_handles[-1])
        now = datetime.datetime.now()
        print('現在時刻: ', now)
        remaining_time = driver.find_element(By.ID, 'time').text
        print('残り時間: ', remaining_time)
        days, hours, minutes, seconds = extract_time_components(remaining_time)
        print(days, hours, minutes, seconds)
        end_time = now + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        print('終了時間: ', end_time)
        d_week = {'Sun': '日', 'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木', 'Fri': '金', 'Sat': '土'}
        key = end_time.strftime('%a')
        w = d_week[key]
        d = end_time.strftime('%Y.%m.%d') + f'（{w}）'+ end_time.strftime('%H:%M:%S')
        print('----------')
        return jsonify({'success': True, 'title': product_title, 'current_price': current_price, 'close_time': d})
    except Exception as e:
        print('商品情報取得でエラー！！！！！！！！: ', e)
        return jsonify({'success': False, 'title': '商品が存在しません.....'})
    finally:
      driver.quit()

def extract_time_components(remaining_time):
    # パターン1: <日>日＋<時>:<分>:<秒>
    pattern1 = re.compile(r'(\d+)日\＋(\d+):(\d+):(\d+)')
    # パターン2: <時>:<分>:<秒>
    pattern2 = re.compile(r'(\d+):(\d+):(\d+)')

    match1 = pattern1.match(remaining_time)
    match2 = pattern2.match(remaining_time)

    if match1:
        days, hours, minutes, seconds = match1.groups()
    elif match2:
        days = '0'
        hours, minutes, seconds = match2.groups()
    else:
        return ''


    return int(days), int(hours) + 9, int(minutes), int(seconds)