"""
此文件为获取各大网站的代理ip
初始逻辑：利用获取的代理ip进行代理，已达到高速爬去代理ip
            当没有代理IP，则用自身ip
数据库存储约束:
    {   '_id':md5(ip:port),
        'ip':127.0.0.1,
        'port':8080,
        'time':0.5,
        'type':https/http
        proxy : 'ip:port'
    }
"""

import requests
from lxml import etree
from fake_useragent import UserAgent
import time
import random, hashlib
from log import Logger
from pymongo import MongoClient


class Public(object):

    def md5(self, id):
        md5 = hashlib.md5()
        md5.update(id.encode('utf-8'))
        id = md5.hexdigest()
        return id

    # 随机获取useragent头
    @property
    def headers(self):
        ua = UserAgent(verify_ssl=False)
        user_agent = ua.random
        headers = {
            'User-Agent': user_agent,
        }
        return headers


# 获取所有的代理ip
class Proxy(Public):

    #连接数据库
    def __init__(self):
        self.logger = Logger('log')
        conn = MongoClient()
        db = conn['oneday']
        self.my_set = db['proxy']

    # 快代理网站
    def KuaiDaiLi(self):
        """
        该网站超出范围的页面显示：Invalid Page
        """
        # 获取当前页
        page = 2873

        while True:
            time.sleep(1)
            proxy_ip = ''  # 获取数据库中的代理ip
            if proxy_ip:
                proxy_ip = 'http://' + proxy_ip
                proxy = {'http': proxy_ip, 'https': proxy_ip}
            else:
                proxy = None
            try:
                url = "https://www.kuaidaili.com/free/inha/%s/" % str(page)
                #输出日志到控制端
                self.logger.dbuglog(url)
                requests.packages.urllib3.disable_warnings()
                response = requests.get(url=url, headers=self.headers, proxies=proxy, verify=False,timeout=5)

                # 第一层判断,状态码是否为200,如果不是,休眠1秒,继续循环
                if response.status_code != 200:
                    self.logger.skiplog(url + '   -----读取错误的url')
                    time.sleep(1)
                    continue

                #防止此代码报异常,导致循环无法退出
                try:
                    response.encoding = response.apparent_encoding
                    response_text = response.text
                    html = etree.HTML(response_text)
                    all_info = html.xpath("//div[@id='list']//tbody/tr")
                    for info in all_info:
                        DB_INFO = {}
                        DB_INFO['ip'] = info.xpath("./td[1]/text()")[0]
                        port = info.xpath("./td[2]/text()")[0]
                        DB_INFO['port'] = int(port)
                        visit_time = info.xpath("./td[6]/text()")[0]
                        DB_INFO['visit_time'] = float(visit_time.replace('秒', ''))
                        DB_INFO['proxy_type'] = info.xpath("./td[4]/text()")[0]
                        ip_port = DB_INFO['ip'] + ':' + port
                        DB_INFO['_id'] = self.md5(ip_port)
                        DB_INFO['ip_port'] = ip_port
                        # 存入数据库
                        self.my_set.save(DB_INFO)
                except Exception as e:
                    pass

                # 判断是否为最后一页,如果是退出
                if len(all_info) < 15:
                    self.logger.skiplog(url + '   -----该url为最后一页')
                    break
            except Exception as e:
                #保存到日志并打印到控制端

                self.logger.errlog(e)
                sleep_time = random.randint(1, 20)
                time.sleep(sleep_time * 0.1)
            finally:
                page += 1


# 过滤并获取可用代理
class Usable_proxy(Public):
    def __init__(self):
        pass

    # 获取测试代理ip
    def get_proxy(self):
        # 从数据库中获取数据
        pass

    # 测试方法
    def check(self, proxy):
        url = 'https://baidu.com'
        try:
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
            res = requests.get(url, headers=self.headers, proxies=proxies, timeout=1)
            return True
        except Exception as e:
            return False

    def save(self):
        proxy = self.get_proxy()
        judge = self.check(proxy)
        if judge:
            # 保存到数据库
            pass


proxy = Proxy()
proxy.KuaiDaiLi()
