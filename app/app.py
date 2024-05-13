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
        close_time = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[3]/section/div/div/table/tbody/tr[13]/td").text
        print('product_title: ', product_title)
        print('current_price: ', current_price)
        return jsonify({'success': True, 'title': product_title, 'current_price': current_price, 'close_time': close_time})
    except Exception as e:
        print('商品情報取得でエラー！！！！！！！！: ', e)
        return jsonify({'success': False, 'title': '商品が存在しません.....'})
    finally:
      driver.quit()

api.add_resource(Bookapi, '/book')

##server run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)