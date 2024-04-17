from selenium import webdriver
from selenium.webdriver.common.by import By
import time

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
login_bar = driver.find_element(By.ID, "login_handle")
# login_bar.send_keys('jackin5beat0803')
login_bar.send_keys('naofumi-okamoto-0803')
next_button = driver.find_element(By.XPATH, "//*[@id='content']/div[1]/div/form/div[1]/div[1]/div[2]/div/button")
next_button.click()
time.sleep(2)

password_bar = driver.find_element(By.ID, "password")
password_bar.send_keys('nnoo00')
login_button = driver.find_element(By.XPATH, "//*[@id='content']/div[1]/div/form/div[2]/div/div[1]/div[2]/div[3]/button")
login_button.click()
time.sleep(2)
driver.quit()

########
# yahoo商品直接
########
# url = 'https://page.auctions.yahoo.co.jp/jp/auction/p1114073453'
# driver.get(url)
# time.sleep(20)
# driver.quit()
########
# yahoo検索
########
# try:
#   contain_all_word = 'synology'
#   at_least_one_contain_word = ''
#   not_included_word = 'ルーター'

#   url = 'https://auctions.yahoo.co.jp/'
#   driver.get(url)
#   # 条件指定をクリック
#   condition_btn = driver.find_element(By.XPATH, '//*[@id="sbn"]/div/a')
#   condition_btn.click()
#   # キーワード入力
#   # すべて含む
#   contain_all = driver.find_element(By.ID, "f0v0")
#   contain_all.send_keys(contain_all_word)
#   # 少なくとも一つ含む
#   at_least_one_contain = driver.find_element(By.ID, "f0v1")
#   at_least_one_contain.send_keys(at_least_one_contain_word)
#   # 含めない
#   not_included = driver.find_element(By.ID, "f0v2")
#   not_included.send_keys(not_included_word)
#   time.sleep(2)

#   # 検索ボタン押下
#   search_btn = driver.find_element(By.XPATH, '//*[@id="btn"]')
#   search_btn.click()
#   time.sleep(2)
#   item_names = driver.find_elements(By.CLASS_NAME, 'Product__title')
#   item_prices = driver.find_elements(By.CLASS_NAME, 'Product__priceInfo')
#   print('-------')
#   for i, name in enumerate(item_names):
#     print(name.text)
#     print(item_prices[i].text)


#   time.sleep(5)
# except Exception as e:
#   print('エラー！！！！！！！！: ', e)

# finally:
#   driver.quit()

########
# メルカリ
########
# try:
#   url = 'https://login.jp.mercari.com/signin?params=client_id%3DbP4zN6jIZQeutikiUFpbx307DVK1pmoW%26code_challenge%3DkUvNDOI1Y-h1h0m7WjfRvkTbFw7_jRmBByyeO9Wy4K4%26code_challenge_method%3DS256%26nonce%3D2uRdf27_cRvF%26redirect_uri%3Dhttps%253A%252F%252Fjp.mercari.com%252Fauth%252Fcallback%26response_type%3Dcode%26scope%3Dmercari%2Bopenid%26state%3DeyJwYXRoIjoiLyIsInJhbmRvbSI6IkNqTi1xSC5Qc2x1RiJ9%26ui_locales%3Dja'
#   driver.get(url)
#   time.sleep(1)
#   login_bar = driver.find_element(By.NAME, "emailOrPhone")
#   login_bar.send_keys('jackin5beat@gmail.com')
#   time.sleep(1)

#   password_bar = driver.find_element(By.NAME, "password")
#   password_bar.send_keys('nnoo00')

#   password_bar.submit()

#   print('OKOKOKOKOK')
#   time.sleep(5)

# except:
#   print('エラー！！！！！！！！')

# finally:
#   driver.quit()
