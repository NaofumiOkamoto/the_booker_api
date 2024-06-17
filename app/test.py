import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def hoge():
  try:
    args = sys.argv
    auction_id = args[1] if len(args) > 1 else '1117361868'
    FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"images/{auction_id}.png")

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
    login_bar = driver.find_element(By.ID, "login_handle")
    login_bar.send_keys('naofumi-okamoto-0803')
    next_button = driver.find_element(By.XPATH, "//*[@id='content']/div[1]/div/form/div[1]/div[1]/div[2]/div/button")
    next_button.click()
    time.sleep(1)
    # パスワード
    password_bar = driver.find_element(By.ID, "password")
    password_bar.send_keys('nnoo00')
    login_button = driver.find_element(By.XPATH, "//*[@id='content']/div[1]/div/form/div[2]/div/div[1]/div[2]/div[3]/button")
    login_button.click()
    time.sleep(1)
    # 商品ページへ
    driver.get(f'https://page.auctions.yahoo.co.jp/jp/auction/{auction_id}')
    time.sleep(1)
    # ポップアップあったら消す
    prMdl = driver.find_element(By.XPATH, "//*[@id='js-prMdl-close']")
    prMdl.click()
    time.sleep(1)
    # 入札するボタン
    bid_button = driver.find_element(By.XPATH, "//*[@id='l-sub']/div[2]/ul/li[1]/div[1]/div[2]/div[2]/div/div/a")
    bid_button.click()
    time.sleep(2)
    # 金額入力
    bid_amount_input = driver.find_element(By.XPATH, "//*[@id='BidModals']/div[2]/div[2]/div[2]/form/div[1]/label/input")
    bid_amount_input.clear()
    bid_amount_input.send_keys('1500')
    time.sleep(1)
    # 確認ボタン
    confirm_button = driver.find_element(By.XPATH, "//*[@id='BidModals']/div[2]/div[2]/div[2]/form/div[3]/span/input")
    confirm_button.click()
    driver.save_screenshot(FILENAME)
    time.sleep(2)
    driver.quit()
  except Exception as e:
    print('エラー: ', e)
    driver.quit()


hoge()
