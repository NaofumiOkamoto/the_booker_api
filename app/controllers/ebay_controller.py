from flask import jsonify, request
import requests
import os
import pytz
import datetime
import random
from models.ebay import EbayToken

def search_item():
  print('search-product 処理開始')
  item_number = request.args.get('item_number')
  uid = request.args.get('uid')
  print('uid', uid)

  now_jst = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
  now_jst_5 = now_jst + datetime.timedelta(days=5)

  return jsonify(
    {
      'item': {
        'product_name': item_number,
        'close_time': now_jst_5,
        'current_price': round(random.uniform(0, 1000), 2)
      }
    })
  ebay_token = EbayToken.query.filter_by(uid=uid).first()
  token = ebay_token.access_token
  print('token', token)

  # url = 'https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search'
  url = 'https://open.api.ebay.com/shopping'
  body = {
    'ItemId': item_number
  }
  headers = {
      'Authorization': f'Bearer {token}'
  }
  response = requests.post(url, headers=headers, params=params)
  # 画像 PictureURL (https://i.ebayimg.com/00/s/MTYwMFgxNjAw/z/A9QAAOSwYvlm25gU/$_57.JPG?set_id=880000500F)
  # 終了時間 EndTime (2024-09-15T15:50:53.000Z)
  # 送料負担 ShippingCostPaidBy (Seller)
  # 現在価格 CurrentPrice (61.0) 
  # ? ConvertedCurrentPrice (61.0)
  # 商品名　Title　(BIG PUN Capital Punishment LOUD 67512-1 2XLP SEALED j)
  # ItemID
  print('response:', response.json())

  return jsonify({'item': response.json()})



def add_item():
  print('#######------########')
  dev_id = 'd5bafe4f-7152-47e7-bed2-c6d4fc8ce0e2'
  app_id = 'naofumio-Booker-SBX-32959e259-dcf1aebc'
  cert_id = 'SBX-2959e2592788-4cbc-4cdd-a004-2b85'
  user_token = 'v^1.1#i^1#r^0#f^0#p^3#I^3#t^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'

  # APIエンドポイント
  url = "https://api.sandbox.ebay.com/ws/api.dll"

  # リクエストヘッダー
  headers = {
      "X-EBAY-API-CALL-NAME": "AddItem",
      "X-EBAY-API-DEV-NAME": dev_id,
      "X-EBAY-API-APP-NAME": app_id,
      "X-EBAY-API-CERT-NAME": cert_id,
      "X-EBAY-API-SITEID": "0",  # USサイト
      "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
      "Content-Type": "text/xml"
  }

  # 出品リクエストボディ (XML形式)
  body = """
  <?xml version="1.0" encoding="utf-8"?>
  <AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
    <RequesterCredentials>
      <eBayAuthToken>{}</eBayAuthToken>
    </RequesterCredentials>
    <Item>
      <Title>Test Auction Item</Title>
      <Description>This is a test auction item.</Description>
      <PrimaryCategory>
        <CategoryID>1234</CategoryID>
      </PrimaryCategory>
      <StartPrice>10.00</StartPrice>
      <CategoryMappingAllowed>true</CategoryMappingAllowed>
      <Country>US</Country>
      <Currency>USD</Currency>
      <DispatchTimeMax>3</DispatchTimeMax>
      <ListingDuration>Days_7</ListingDuration>
      <ListingType>Chinese</ListingType>
      <ConditionID>1000</ConditionID>
      <PostalCode>95125</PostalCode>
      <Quantity>1</Quantity>

      <ItemSpecifics>
        <NameValueList>
          <Name>Brand</Name>
          <Value>YourBrand</Value>
        </NameValueList>
        <NameValueList>
          <Name>Type</Name>
          <Value>YourType</Value>
        </NameValueList>
      </ItemSpecifics>

      <ReturnPolicy>
        <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
        <RefundOption>MoneyBack</RefundOption>
        <ReturnsWithinOption>Days_30</ReturnsWithinOption>
        <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
      </ReturnPolicy>
      <ShippingDetails>
        <ShippingType>Flat</ShippingType>
        <ShippingServiceOptions>
          <ShippingServicePriority>1</ShippingServicePriority>
          <ShippingService>USPSPriority</ShippingService>
          <ShippingServiceCost>0.00</ShippingServiceCost>
        </ShippingServiceOptions>
      </ShippingDetails>
      <Site>US</Site>
    </Item>
  </AddItemRequest>
  """.format(user_token)


  # リクエスト送信
  response = requests.post(url, headers=headers, data=body)

  # レスポンス確認
  print('res.text', response.text)
  return jsonify({'result': 'a'})
