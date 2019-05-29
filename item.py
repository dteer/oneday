import requests
from lxml import etree
import re
from fake_useragent import UserAgent
from pymongo import MongoClient
import json,datetime,hashlib,time,random


class spider_money(object):

    def __init__(self,dbname,colletion):
        self.data = {}
        self.my_set = None
        self.dbname = dbname
        self.colletion = colletion
        self.__conn_db()

    #随机获取useragent头
    @property
    def get_hearders(self):
        ua = UserAgent(verify_ssl=False)
        user_agent = ua.random
        headers = {
            'User-Agent':user_agent,
        }
        return headers

    #随机获取代理IP
    @property
    def get_agent(self):
        all_agent = []
        for i in range(1,5):
            agent = []
            if all_agent:
                prox_ip = 'http://'+ all_agent[i][0]+':'+str(all_agent[i][1])
                prox_ips = 'https://'+ all_agent[i][0]+':'+str(all_agent[i][1])
                proxies = {'http': prox_ip ,'https':prox_ips}
            else:
                proxies = None
            print(proxies)
            url = "https://www.kuaidaili.com/free/inha/%s/" % str(i)
            response = requests.get(url=url, headers=self.get_hearders,proxies=proxies,verify=False)
            response.encoding = response.apparent_encoding
            html = etree.HTML(response.text)
            ip = html.xpath("//div[@id='list']//tbody/tr/td[1]/text()")
            port = html.xpath("//div[@id='list']//tbody/tr/td[2]/text()")
            port = [int(p) for p in port]
            res_time = html.xpath("//div[@id='list']//tbody/tr/td[6]/text()")
            res_time = [float(res.replace('秒', '')) for res in res_time]
            agent = list(zip(ip, port, res_time))
            all_agent +=agent
        return all_agent

    #连接数据库
    def __conn_db(self):
        conn = MongoClient('127.0.0.1', 27017)
        db = conn[self.dbname]
        self.my_set = db[self.colletion]


    #入口,获取所有的期数
    def get_term(self):
        response = requests.get('http://kaijiang.500.com/shtml/ssq/19059.shtml?0_ala_baidu/',headers=self.get_hearders)
        # 自动解码
        response.encoding = response.apparent_encoding
        html = etree.HTML(response.text)
        # 获取所有的期数
        term = html.xpath("//div[@class='iSelectList']/a/text()")
        return term

    # 获取对应的数据
    def get_data(self,num):
        url = 'http://kaijiang.500.com/shtml/ssq/%s.shtml' % str(num)
        response = requests.get(url, headers=self.get_hearders)
        response.encoding = response.apparent_encoding
        html = etree.HTML(response.text)

        # 开奖号码
        num_sort = html.xpath("//div[@class='ball_box01']/ul/li/text()")
        # 出球顺序
        num_real = html.xpath("//td[@align='left']/table/tr[2]/td[2]/text()")
        if num_real:
            num_real = re.findall('\d+', num_real[0])
        else:
            num_real = '错误'
        # 销量和奖池
        sum = html.xpath("//div[@class='kjxq_box02']//span[@class='cfont1 ']/text()")
        sale_money = sum[0].replace(',', '').replace('元', '')
        pool_money = sum[1].replace(',', '').replace('元', '')
        sum_money = {'sale_money':sale_money,'pool_money':pool_money}

        # 中奖项和中奖注数 单注奖金
        all_prize = []
        for i in range(3, 9):
            num_prize = html.xpath("//table[@class='kj_tablelist02'][2]//tr[%s]/td/text()" % i)
            num_prize = [re.findall('[^\s]+', res)[0].replace(',', '') for res in num_prize]
            dic = {
                '奖项': num_prize[0],
                '注数': int(num_prize[1]),
                '每注奖': int(num_prize[2]),
            }
            all_prize.append(dic)

        #保存url的md5值作为id防止重复数据
        md5 = hashlib.md5()
        md5.update(url.encode('utf-8'))
        url = md5.hexdigest()
        self.data = {
            '_id':url,
            '期数':num,
            '开奖号码':num_sort,
            '出球顺序':num_real,
            '总金额':sum_money,
            '详情':all_prize,
        }

        return url,self.data

    #查询数据库是否存在此数据
    def check(self,url):
        judge = self.my_set.find_one({'_id':url})
        return judge

    # 保存到mongodb数据库
    def save_data(self,url,data):
        #第一种方法:查询数据是否存在,存在则更新
        # judge_data = self.check(url)
        # if judge_data:
        #     data = {'$set':data}
        #     self.my_set.update_one(judge_data,data)
        # else:
        #     self.my_set.insert(data)

        #第二种方法,mongodb有一个方法save可以直接覆盖_id相等的数据
        self.my_set.save(data)


# if __name__ == '__main__':
#     start_time = datetime.datetime.now()
#     lottery_obj = spider_money('mydb','lottery')
#     term = lottery_obj.get_term()
#     term.pop(0)
#     for i in term[766:]:
#         print(i)
#         url,data = lottery_obj.get_data(i)
#         lottery_obj.save_data(url,data)
#         t = random.randint(0,5)
#         time.sleep(t*0.1)
#     print(datetime.datetime.now()-start_time)



t= spider_money('d','d')
ds = t.get_agent
print(len(ds))