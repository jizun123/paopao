import requests
from lxml import etree
import time
import random
import pymysql


class FundSpider:

    def __init__(self):
        self.url = 'http://www.southmoney.com/fund/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
        # 连接数据库
        self.db = pymysql.connect(
            'localhost',
            'root',
            'yiwang21',
            'paopao',
            charset='utf8',
        )
        # 创建游标对象
        self.cur = self.db.cursor()
        # 创建存放数据的空列表
        self.all_fund_list = []

    def grt_html(self):
        try:
            html = requests.get(url=self.url, headers=self.headers,
                                timeout=3)
            html.encoding = 'gb2312'
            html = html.text
            # print(html)
            return html
        except Exception as e:
            print("请求失败")
            print(e)

    # 数据处理函数
    def parse_html(self):
        html = self.grt_html()
        p = etree.HTML(html)
        r_list = p.xpath('//table[@class="tbllist"]/tr')
        # print(r_list)
        self.save_funds(r_list)

    # 保存数据
    def save_funds(self, fund_list):
        for data in fund_list:
            if len(data.xpath('.//td/text()')) < 9:
                pass
            else:
                t = (
                    data.xpath('.//td/text()')[1].strip(),
                    data.xpath('.//td/nobr/a/text()')[0].strip(),
                    float(data.xpath('.//td/text()')[4].strip()),
                    float(data.xpath('.//td/text()')[3].strip()),
                    float(data.xpath('.//td/text()')[6].strip()),
                    float(data.xpath('.//td/text()')[7].strip()[:-1:])
                )
                self.all_fund_list.append(t)

    def run(self):
        self.parse_html()
        print(len(self.all_fund_list))
        print(self.all_fund_list)

         # 插入sql语句
        ins = 'insert into funds( funds_id, funds_name, funds_accu, funds_day_val, funds_day_rate, funds_year_rate) values ( %s, %s, %s, %s, %s, %s)'
        self.cur.executemany(ins, self.all_fund_list)
        self.db.commit()
        # 关闭游标对象
        self.cur.close()
        # 断开数据库的连接
        self.db.close()


if __name__ == '__main__':
    fund = FundSpider()
    fund.run()
