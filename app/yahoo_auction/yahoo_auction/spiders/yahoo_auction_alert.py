import scrapy


class YahooAuctionAlertSpider(scrapy.Spider):
    tart_urls = ["https://auctions.yahoo.co.jp"]
    name = 'yahoo_auction_alert'
    allowed_domains = ['auctions.yahoo.co.jp']
    # start_urls = ['https://auctions.yahoo.co.jp//search/search?va=wtaps+帽子']

    def __init__(self, feed=None, *args, **kwargs):
        print('---------------init start----------------')
        super(YahooAuctionAlertSpider, self).__init__(*args, **kwargs) #引数を受け取るための継承
        va = 'synology' # すべて含む
        ve = 'DS' # 除外ワード
        aucminprice = 1000 # 現在価格の最低額
        aucmaxprice = 40000 # 現在価格の最高額
        # istatus: 商品の状態 #1 未使用 #2 中古 #3 未使用に近い #4 目立った傷や汚れなし #5 やや傷や汚れあり #6 傷や汚れあり #7 全体的に状態が悪い
        # privacy_delivery: 匿名配送 #0 指定なし #1 匿名配送のみ
        mode = 2 # 一覧の表示形式 #1簡単な一覧 #2出品者も少し見えるやつ  #4?
        
        self.start_urls = [f'https://auctions.yahoo.co.jp//search/search?va={va}&ve={ve}&aucminprice={aucminprice}&aucmaxprice={aucmaxprice}&istatus=2&privacy_delivery=1&mode={mode}']
        print('---------------init end----------------')

    def parse(self, response):
        products = response.xpath('//ul[@class="Products__items"]/li/div[@class="Product__detail"]')

        print('---------------parse start----------------')

        for product in products:
            title = product.xpath('./div/div/h3/a/text()').get()
            price = product.xpath('./div/div/div[@class="Product__priceInfo"]/span[1]/span[2]/text()').get()
            price2 = product.xpath('./div/div/div[@class="Product__priceInfo"]/span[2]/span[2]/text()').get()
            parcent = product.xpath('./div/div[@class="Product__infoCell Product__infoCell--right"]/div/div/div[@class="Product__rating"]/span/text()').get()
            # yield {
            #     'title': product.xpath('./h3/a/text()').get(),
            #     'price': product.xpath('./div[@class="Product__priceInfo"]/span[1]/span[2]/text()').get(),
            #     'price2': product.xpath('./div[@class="Product__priceInfo"]/span[2]/span[2]/text()').get(),
            # }
            print(title, price, price2, parcent)
        print('1page-len: ', len(products))

        all_len = response.xpath('//div[@class="Tab__itemInner"]/span[2]/text()').get()
        yield {
            'len': all_len
        }
        print('url: ', self.start_urls)


        print('---------------parse end----------------')
