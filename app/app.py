import datetime
import time
import pytz
import re
from celery_utils import make_celery
from flask import Flask,request,jsonify,send_file
from database import init_db
from flask_restful import Api
from flask_marshmallow import Marshmallow
from models.book import Book, Bookapi
from test_scraping import hoge
from database import db

from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'
celery = make_celery(app)
ma = Marshmallow(app)
api = Api(app)
init_db(app)

@celery.task(name="app.run_test")
def run_test(auction_id, bid_first_amount):
    with app.app_context():
        print('run_test auction_id: ', auction_id)
        from test_scraping import hoge
        result = hoge(auction_id, bid_first_amount)
        return f"Task completed at {datetime.datetime.now().isoformat()} - Result: {result}"

@app.route('/schedule', methods=['GET'])
def schedule_task():
    # book = Book.query.get(42)
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    now_jst_5 = now_jst + datetime.timedelta(minutes=5)
    print('now_jst', now_jst)
    print('now_jst_5', now_jst_5)
    datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    books = Book.query.filter(
        Book.close_time > now_jst,
        Book.close_time < now_jst_5,
        Book.bid_time == None
    ).all()

    if not books:
        return jsonify({"error": "Book not found"}), 404

    tasks = []
    for book in books:
        print(book.to_dict())
        close_time = book.close_time

        if close_time.tzinfo is None:
            close_time = jst.localize(close_time)
        else:
            close_time = close_time.astimezone(jst)
        
        delay = (close_time - now_jst).total_seconds()
        print(close_time)
        print(now_jst)
        print(delay)
        if delay < 0:
            return jsonify({"error": "close_time is in the past"}), 400
        
        print(f'-----start run_test.apply_async--{book.auction_id}------')
        task = run_test.apply_async(args=[book.auction_id, book.first_bid_amount], countdown=delay) 
        print('-----end run_test.apply_async--------')
        tasks.append(task.id)
        print(task.id)

    return jsonify({'tasks': tasks, 'books': [book.to_dict() for book in books]}), 202

@app.route("/api/check_prod", methods=["GET"])
def index():
    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
                command_executor = 'http://the_booker_api-selenium-1:4444/wd/hub',
                options = options
                )

    # driver.implicitly_wait(1)
    id = request.args.get('id')
    url = f'https://page.auctions.yahoo.co.jp/jp/auction/{id}'
    print('-------driver get start-------')
    try:
        driver.get(url)
        product_title = driver.find_element(By.XPATH, "//*[@id='ProductTitle']/div/h1").text
        print('商品名: ', product_title)
        current_price = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[1]/div[1]/div[2]/dl/div[1]/dd").text
        print('現在価格: ', current_price)

        # 更新情報があると階層が変わるため
        # li3_text = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[3]").text
        # if li3_text == '更新情報':
        #     liNum = 'li[4]'
        # else:
        #     liNum = 'li[3]'
        # tr[11] ~ tr[13] に終了日時がありそうなので以下のような取り方にした
        # th11 = driver.find_element(By.XPATH, f"//*[@id='l-sub']/div[2]/ul/{liNum}/section/div/div/table/tbody/tr[11]/th").text
        # td11 = driver.find_element(By.XPATH, f"//*[@id='l-sub']/div[2]/ul/{liNum}/section/div/div/table/tbody/tr[11]/td").text
        # th12 = driver.find_element(By.XPATH, f"//*[@id='l-sub']/div[2]/ul/{liNum}/section/div/div/table/tbody/tr[12]/th").text
        # td12 = driver.find_element(By.XPATH, f"//*[@id='l-sub']/div[2]/ul/{liNum}/section/div/div/table/tbody/tr[12]/td").text
        # th13 = driver.find_element(By.XPATH, f"//*[@id='l-sub']/div[2]/ul/{liNum}/section/div/div/table/tbody/tr[13]/th").text
        # td13 = driver.find_element(By.XPATH, f"//*[@id='l-sub']/div[2]/ul/{liNum}/section/div/div/table/tbody/tr[13]/td").text
        # for tr in [[th11, td11], [th12, td12], [th13, td13]]:
        #     print(tr)
        #     if tr[0] == '終了日時':
        #         close_time = tr[1]

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
        end_time = now + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        print('終了時間: ', end_time)
        d_week = {'Sun': '日', 'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木', 'Fri': '金', 'Sat': '土'}
        key = end_time.strftime('%a')
        w = d_week[key]
        d = end_time.strftime('%Y.%m.%d') + f'（{w}）'+ end_time.strftime('%H:%M:%S')
        return jsonify({'success': True, 'title': product_title, 'current_price': current_price, 'close_time': d})
    except Exception as e:
        print('商品情報取得でエラー！！！！！！！！: ', e)
        return jsonify({'success': False, 'title': '商品が存在しません.....'})
    finally:
      driver.quit()

@app.route("/api/get_img", methods=["GET"])
def get_img():
    try:
        id = request.args.get('auctionId')
        filename = f'images/{id}.png'
        print(filename)
        return send_file(filename, mimetype='image/jpeg')

    except Exception as e:
        print('画像なし')
        return jsonify({'status': ''}), 404



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

api.add_resource(Bookapi, '/book')

##server run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)