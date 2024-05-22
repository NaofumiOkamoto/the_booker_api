import datetime
import time
import re
from flask import Flask,request,jsonify
from database import init_db
from flask_restful import Api
from flask_marshmallow import Marshmallow
from models.book import Bookapi

# 
from selenium import webdriver
from selenium.webdriver.common.by import By
# import time

app = Flask(__name__)
app.config.from_object('config.Config')
ma = Marshmallow(app)
api = Api(app)
init_db(app)

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
        current_price = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[1]/div[1]/div[2]/dl/div[1]/dd").text

        # 更新情報があると階層が変わるため
        li3_text = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[3]").text
        if li3_text == '更新情報':
            liNum = 'li[4]'
        else:
            liNum = 'li[3]'
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
        time.sleep(1.5)
        driver.switch_to.window(driver.window_handles[-1])
        now = datetime.datetime.now()
        remaining_time = driver.find_element(By.ID, 'time').text
        pattern = r'\d+'
        matches = re.findall(pattern, remaining_time)
        days, hours, minutes, seconds = matches
        end_time = now + datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
        d_week = {'Sun': '日', 'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木', 'Fri': '金', 'Sat': '土'}
        key = end_time.strftime('%a')
        w = d_week[key]
        d = end_time.strftime('%Y.%m.%d') + f'（{w}）'+ end_time.strftime('%H:%M:%S')
        print('残り時間: ', remaining_time)
        print('現在時刻: ', now)
        print('終了時間: ', end_time)
        print('商品名: ', product_title)
        print('現在価格: ', current_price)
        return jsonify({'success': True, 'title': product_title, 'current_price': current_price, 'close_time': d})
    except Exception as e:
        print('商品情報取得でエラー！！！！！！！！: ', e)
        return jsonify({'success': False, 'title': '商品が存在しません.....'})
    finally:
      driver.quit()

api.add_resource(Bookapi, '/book')

##server run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)