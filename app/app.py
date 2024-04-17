from flask import Flask,request,jsonify
from database import init_db
import models

# 
from selenium import webdriver
from selenium.webdriver.common.by import By
# import time

app = Flask(__name__)
app.config.from_object('config.Config')
init_db(app)

@app.route("/api/check_prod", methods=["GET"])
def index():
    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
                command_executor = 'http://selenium:4444/wd/hub',
                options = options
                )

    # driver.implicitly_wait(1)
    id = request.args.get('id')
    url = f'https://page.auctions.yahoo.co.jp/jp/auction/{id}'
    print('-------driver get start-------')
    try:
        driver.get(url)
        productTitle = driver.find_element(By.XPATH, "//*[@id='ProductTitle']/div/h1")
        print('productTitle: ', productTitle.text)
        title = productTitle.text
        return jsonify({'title': title})
    except Exception as e:
        print('エラー！！！！！！！！: ', e)
        return jsonify({'title': '商品が存在しません'})
    finally:
      driver.quit()


##server run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)