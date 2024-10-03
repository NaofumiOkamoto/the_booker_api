from flask import jsonify, request
import requests
import os
from datetime import datetime, timedelta
from models.ebay import EbayToken
import base64
from models.book import Book
import xml.etree.ElementTree as ET
import pytz
from database import db
from dateutil import parser

def get_ebay_token(uid):
  ebay_token = EbayToken.query.filter_by(uid=uid).first()
  token = ebay_token.access_token
  refresh_token = ebay_token.refresh_token
  CLIENT_ID = os.getenv('CLIENT_ID')
  CLIENT_SECRET = os.getenv('CLIENT_SECRET')

  expiration_time = ebay_token.updated_at + timedelta(seconds=7000)
  token_expiration_time = expiration_time.replace(tzinfo=None)
  japan_tz = pytz.timezone('Asia/Tokyo')
  current_time = datetime.now(japan_tz).replace(tzinfo=None)
  print('token_expiration_time', token_expiration_time)
  print('current_time', current_time)

  # アクセストークンが期限切れかどうかを確認
  if token_expiration_time < current_time:
      print("アクセストークンが期限切れです。リフレッシュトークンを使用して新しいアクセストークンを取得します。")
      # リフレッシュトークンを使用して新しいアクセストークンを取得
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}'# Base64エンコードが必要です
      }
      data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'scope': 'https://api.ebay.com/oauth/api_scope'
      }
      response = requests.post('https://api.ebay.com/identity/v1/oauth2/token', headers=headers, data=data)

      if response.status_code == 200:
          new_access_token = response.json()['access_token']
          expires_in = response.json()['expires_in']
          print(f"有効期限（秒）: {expires_in}")

          # DBのアクセストークンを更新
          ebay_token.access_token = new_access_token
          ebay_token.updated_at = current_time
          db.session.commit()
          return new_access_token
      else:
          print(f"アクセストークンの再取得に失敗しました。エラー: {response.text}")
  else:
      print("アクセストークンはまだ有効です。")
      return token


def search_item():
  print('search-product 処理開始')
  item_number = request.args.get('item_number')
  uid = request.args.get('uid')
  ship_to = request.args.get('ship_to')
  print(ship_to)

  # すでに予約済みかを確認
  item = Book.query.filter_by(user_id=uid, item_number=item_number).first()
  if item != None:
    return jsonify({ 'item': 'duplicate' })

  token = get_ebay_token(uid)
  url = f'https://api.ebay.com/buy/browse/v1/item/v1|{item_number}|0'
  headers = {
    "Authorization": f'Bearer {token}',  # Replace with your actual access token
    "Content-Type": "application/json",
    "X-EBAY-C-ENDUSERCTX": f"contextualLocation=country={ship_to},zip=",
    # 'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'  # 英語のマーケットプレイス（US）
  }
  response = requests.get(url, headers=headers)
  result = response.json()

  if (result.get('errors')):
    print(result.get('errors'))
    return jsonify({ 'item': None })

  # item_id = result['itemId']
  current_price = 0
  current_price_jp = 0
  currency = 'USD'
  shipping_cost = 0
  shippingOptions = None
  print(result)
  title = result['title']
  currentBidPrice = result.get('currentBidPrice')
  if currentBidPrice == None:
    return jsonify({ 'item': 'not_auction' })
    # current_price = currentBidPrice.get('convertedFromValue')
  current_price = currentBidPrice.get('value')
  currency = currentBidPrice.get('currency')
  image_url = result['itemId']
  end_time = result.get('itemEndDate') # APIでは 2024-10-01T13:31:02.000Zのように世界時間で取得される
  shippingOptions = result.get('shippingOptions')
  # 日本へ配送されない場合があります。配送方法については、商品説明を読むか、出品者にお問い合わせください
  # ↑の時は shippingOptions がないっぽい
  if shippingOptions != None:
    shipping_cost = shippingOptions[0]['shippingCost']['value']
  image_url = result['image']['imageUrl']

  return jsonify({ 'item': {
      'title': title,
      'end_time': end_time,
      'current_price': current_price,
      'currency': currency,
      'shipping_cost': shipping_cost,
      'image_url': image_url,
      'shippingOptions': shippingOptions,
    }
  })

def get_watch_list():
    print('get watch list')
    uid = request.args.get('uid')
    token = get_ebay_token(uid)

    # Trading API の GetMyEbayBuying
    EBAY_API_URL = "https://api.ebay.com/ws/api.dll"
    HEADERS = {
      'X-EBAY-API-CALL-NAME': 'GetMyeBayBuying',
      'X-EBAY-API-SITEID': '0',  # 0 = US site
      'X-EBAY-API-COMPATIBILITY-LEVEL': '967',  # APIのバージョン
      'X-EBAY-API-IAF-TOKEN': token,
      'Content-Type': 'text/xml'
    }
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <GetMyeBayBuyingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
      <RequesterCredentials>
        <eBayAuthToken>{token}</eBayAuthToken>
      </RequesterCredentials>
      <WatchList>
        <Include>true</Include>
      </WatchList>
    </GetMyeBayBuyingRequest>"""

    try:
      response = requests.post(EBAY_API_URL, headers=HEADERS, data=body)

      # XMLをJSON形式に変換
      root = ET.fromstring(response.text)
      # eBayのネームスペース
      ns = {'ns': 'urn:ebay:apis:eBLBaseComponents'}

      ack = root.find('.//ns:Ack', ns).text
      if (ack != 'Success'):
        print('見つからず')
        print(response.text)
        return jsonify({'item': None})
      items = []
      # ItemArray内のItem情報を抽出
      # print(response.text)
      for item in root.findall('.//ns:Item', ns):
        print('itemId: ', item.find('ns:ItemID', ns).text)
        print('ListingType: ', item.find('ns:ListingType', ns).text)
        end_time = parser.parse(item.find('.//ns:EndTime', ns).text).replace(tzinfo=None)
        now = datetime.now().replace(tzinfo=None)
        if end_time < now:
          continue
        if item.find('ns:ListingType', ns).text != 'Auction':
          continue
        item_info = {
          'item_number': item.find('ns:ItemID', ns).text,
          'title': item.find('ns:Title', ns).text,
          'StartTime': item.find('.//ns:StartTime', ns).text,
          'end_time': item.find('.//ns:EndTime', ns).text,
          'ViewItemURL': item.find('.//ns:ViewItemURL', ns).text,
          'shipping_cost': item.find('.//ns:ShippingServiceCost', ns).text if 
            item.find('.//ns:ShippingServiceCost', ns) is not None else 0,
            #     item.find('.//ns:ConvertedCurrentPrice', ns) is not None else item.find('.//ns:StartPrice', ns).text,
                                                                    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # AttributeError: 'NoneType' object has no attribute 'text'
          'current_price': item.find('.//ns:ConvertedCurrentPrice', ns).text if 
            item.find('.//ns:ConvertedCurrentPrice', ns) is not None else item.find('.//ns:StartPrice', ns).text,
          'image_url': item.find('.//ns:GalleryURL', ns).text
        }
        items.append(item_info)

      return jsonify({
        'watchlist': items
      })
    except Exception as e:
      print('ウォッチリスト取得エラー', e)

# def search_single_item():
#   print('search-product 処理開始')
#   item_number = request.args.get('item_number')
#   uid = request.args.get('uid')
#   print('uid', uid)

#   ebay_token = EbayToken.query.filter_by(uid=uid).first()
#   token = ebay_token.access_token
#   print('token', token)

#   # url = 'https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search'
#   url = 'https://open.api.ebay.com/shopping'
#   body = {
#     'ItemId': item_number
#   }
#   body = f'''<?xml version="1.0" encoding="utf-8"?>
#     <GetSingleItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
#       <ItemID>{item_number}</ItemID>
#       <IncludeSelector>ItemSpecifics,ShippingCosts</IncludeSelector>
#     </GetSingleItemRequest>
#   '''
#   print(body)
#   headers = {
#     'X-EBAY-API-IAF-TOKEN': token,  # Bearer token
#     'X-EBAY-API-SITE-ID': '0',  # Site ID (0 for the US)
#     'X-EBAY-API-CALL-NAME': 'GetSingleItem',
#     'X-EBAY-API-VERSION': '863',
#     'X-EBAY-API-REQUEST-ENCODING': 'xml'
#   }
#   response = requests.post(url, headers=headers, data=body)
#   print(response.text)
#   root = ET.fromstring(response.text)
# # eBayのネームスペース
#   ns = {'ebay': 'urn:ebay:apis:eBLBaseComponents'}

#   # 必要な情報をネームスペースを使って検索 (例: 商品名、現在価格など)
#   ack = root.find('.//ebay:Ack', ns).text
#   if (ack != 'Success'):
#     print('見つからず')
#     return jsonify({'item': None})

#   title = root.find('.//ebay:Title', ns).text
#   end_time = root.find('.//ebay:EndTime', ns).text
#   current_price = root.find('.//ebay:ConvertedCurrentPrice', ns).text
#   currency = root.find('.//ebay:ConvertedCurrentPrice', ns).attrib['currencyID']
#   shipping_cost = root.find('.//ebay:ShippingServiceCost', ns).text
#   shipping_cost_curerncy = root.find('.//ebay:ShippingServiceCost', ns).attrib['currencyID']
#   img_url = root.find('.//ebay:PictureURL', ns).text
#   print(f"商品名: {title}")
#   print(f"現在価格: {current_price} {currency}")
#   print(f"終了時間: {end_time}")
#   print(f"送料: {shipping_cost} {shipping_cost_curerncy}")
#   print(f"画像: {img_url}")

#   # return jsonify({'item': response.json()})
#   return jsonify({ 'item': {
#       'title': title,
#       'end_time': end_time,
#       'current_price': current_price,
#       'currency': currency,
#       'shipping_cost': shipping_cost,
#       'img_url': img_url,
#     }
#   })



# def add_item():
#   print('#######------########')
#   dev_id = 'd5bafe4f-7152-47e7-bed2-c6d4fc8ce0e2'
#   app_id = 'naofumio-Booker-SBX-32959e259-dcf1aebc'
#   cert_id = 'SBX-2959e2592788-4cbc-4cdd-a004-2b85'
#   user_token = 'v^1.1#i^1#r^0#f^0#p^3#I^3#t^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'

#   # APIエンドポイント
#   url = "https://api.sandbox.ebay.com/ws/api.dll"

#   # リクエストヘッダー
#   headers = {
#       "X-EBAY-API-CALL-NAME": "AddItem",
#       "X-EBAY-API-DEV-NAME": dev_id,
#       "X-EBAY-API-APP-NAME": app_id,
#       "X-EBAY-API-CERT-NAME": cert_id,
#       "X-EBAY-API-SITEID": "0",  # USサイト
#       "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
#       "Content-Type": "text/xml"
#   }

#   # 出品リクエストボディ (XML形式)
#   body = """
#   <?xml version="1.0" encoding="utf-8"?>
#   <AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
#     <RequesterCredentials>
#       <eBayAuthToken>{}</eBayAuthToken>
#     </RequesterCredentials>
#     <Item>
#       <Title>Test Auction Item</Title>
#       <Description>This is a test auction item.</Description>
#       <PrimaryCategory>
#         <CategoryID>1234</CategoryID>
#       </PrimaryCategory>
#       <StartPrice>10.00</StartPrice>
#       <CategoryMappingAllowed>true</CategoryMappingAllowed>
#       <Country>US</Country>
#       <Currency>USD</Currency>
#       <DispatchTimeMax>3</DispatchTimeMax>
#       <ListingDuration>Days_7</ListingDuration>
#       <ListingType>Chinese</ListingType>
#       <ConditionID>1000</ConditionID>
#       <PostalCode>95125</PostalCode>
#       <Quantity>1</Quantity>

#       <ItemSpecifics>
#         <NameValueList>
#           <Name>Brand</Name>
#           <Value>YourBrand</Value>
#         </NameValueList>
#         <NameValueList>
#           <Name>Type</Name>
#           <Value>YourType</Value>
#         </NameValueList>
#       </ItemSpecifics>

#       <ReturnPolicy>
#         <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
#         <RefundOption>MoneyBack</RefundOption>
#         <ReturnsWithinOption>Days_30</ReturnsWithinOption>
#         <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
#       </ReturnPolicy>
#       <ShippingDetails>
#         <ShippingType>Flat</ShippingType>
#         <ShippingServiceOptions>
#           <ShippingServicePriority>1</ShippingServicePriority>
#           <ShippingService>USPSPriority</ShippingService>
#           <ShippingServiceCost>0.00</ShippingServiceCost>
#         </ShippingServiceOptions>
#       </ShippingDetails>
#       <Site>US</Site>
#     </Item>
#   </AddItemRequest>
#   """.format(user_token)


#   # リクエスト送信
#   response = requests.post(url, headers=headers, data=body)

#   # レスポンス確認
#   print('res.text', response.text)
#   return jsonify({'result': 'a'})
