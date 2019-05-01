import requests
import json
import difflib
import os
import pickle
import sqlite3
import time
from Product import Product


class ShopeeCrawler(object):
    def __init__(self, categoey):
        self.category_name = category_filter(categoey)
        self.db = sqlite3.connect('product.db')
        self.category_dict = pickle.load(open('{}.pkl'.format(self.category_name), 'rb'))
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                          '(KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'
        self.sub_category_lst = self.category_dict['sub']
        self.item_lst_url = 'https://shopee.tw/api/v2/search_items/?by=price&categoryids={}&limit=50' \
                            '&match_id={}&newest={}&order=asc&page_type=search&price_max={}&price_min={}'

    def get_item_lst(self):
        cur = self.db.cursor()
        product = Product(None, [])
        for sub_category in self.sub_category_lst:
            sub_category_id = sub_category['catid']
            for sub_sub_category in sub_category['sub_sub']:
                sub_sub_category_id = sub_sub_category['catid']
                price = 0
                while price < 100:
                    item = True
                    newest = 0
                    while item:
                        req = requests.get(
                            self.item_lst_url.format(sub_sub_category_id, sub_category_id, newest, price + 10,
                                                     price + 1),
                            headers={'user-agent': self.user_agent})
                        item_dict = json.loads(req.content.decode('utf-8'))
                        item = item_dict['items']
                        if len(item) == 0:
                            break
                        for each_item in item:
                            result = parse_item(each_item['shopid'], each_item['itemid'])
                            print(result)
                            product_id = str(result[0]) + '_' + str(result[1])
                            cur.execute("INSERT or REPLACE into product (id,name,description) VALUES (?,?,?)",
                                        (product_id, result[2], result[3]))
                            self.db.commit()
                            product.data.append(result)
                        newest += 50
                    price += 50


def parse_item(shopid, itemid):
    item_url = 'https://shopee.tw/api/v2/item/get?itemid={}&shopid={}'.format(itemid, shopid)
    req = requests.get(item_url,
                       headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                              '(KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'})
    item_result = json.loads(req.content.decode('utf-8'))
    return shopid, itemid, item_result['item']['name'], item_result['item']['description']


# 輸入字串比對，只是為了以防萬一輸入錯誤
# 輸入妝化品也會搜尋到化妝品
def category_filter(q):
    category_url = 'https://shopee.tw/api/v1/category_list/'
    req = requests.get(category_url)
    category_dict = json.loads(req.content.decode('utf-8'))
    match_lst = [difflib.SequenceMatcher(a=q, b=cate['main']['display_name']).ratio() for cate in category_dict]
    # if same find first
    max_one = match_lst.index(max(match_lst))
    category_name = category_dict[max_one]['main']['display_name']
    if not os.path.exists('{}.pkl'.format(category_name)):
        pickle.dump(category_dict[max_one], open('{}.pkl'.format(category_name), 'wb'))
    return category_name


if __name__ == '__main__':
    start = time.time()
    shopee = ShopeeCrawler('美妝保健')
    shopee.get_item_lst()
    end = time.time()
    print(end - start)
