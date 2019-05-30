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

    def __init__(self):
        self.logger = Logger('log')
        conn = MongoClient()
        db = conn['oneday']
        self.my_set = db['proxy']

    def __repeat_load(self, url, Load_count, proxy=None):
        """
        当前url重连允许次数
        :param url: 当前url
        :param Load_count: 允许当前连续错误次数
        :param proxy: 代理ip
        :return:是否达到最大错误连接次数，bool值
        """
        CUR_COUNT = 1
        while True:
            try:
                response = requests.get(url=url, headers=self.headers, proxies=proxy, verify=False, timeout=5)
                if response.status_code == 200:
                    self.logger.skiplog(url + '   -----url重连次数：%s' % CUR_COUNT)
                    return True
                else:
                    if CUR_COUNT >= Load_count:
                        self.logger.skiplog(url + '   -----url退出重连，次数超过最大值：%s' % CUR_COUNT)
                        return False
                    else:
                        time.sleep(1)
                        CUR_COUNT += 1
                        self.logger.skiplog(url + '   -----url重连次数：%s' % CUR_COUNT)
            except Exception as e:
                if CUR_COUNT >= Load_count:
                    self.logger.skiplog(url + '   -----url退出重连，次数超过最大值：%s' % CUR_COUNT)
                    return False
                CUR_COUNT += 1

    def __all_repeat_load(self, judge, del_count, all_count):
        """
        该网站连续错误访问允许次数
        :param judge:当前url访问情况，bool值
        :param del_count:允许该网站连续url错误访问剩余次数
        :param all_count:允许该网站连续url错误访问总次数
        :return:允许该网站连续url错误访问剩余次数
        """
        if judge:
            return all_count
        else:
            del_count -= 1
            return del_count

    # 当前url重连允许次数和连续url错误访问允许次数
    def judge_status(self, url, Cur_count, del_count, ALL_count, proxy=None):

        """
        :param url: 当前url
        :param del_count: 允许该网站连续url错误访问剩余次数
        :param Cur_count: 允许当前url错误访问次数
        :param ALL_count: 访问连续url的错误允许总次数
        :param proxy:代理ip
        :return:允许该网站连续url错误访问剩余次数
        """
        judge = self.__repeat_load(url, Cur_count, proxy)
        count = self.__all_repeat_load(judge, del_count, ALL_count)
        return count

    # 设置代理
    @property
    def proxy(self):
        """
        从数据库中获取数据，并返回
        :return:代理ip
        """
        proxy_ip = ''  # 获取数据库中的代理ip
        if proxy_ip:
            proxy_ip = 'http://' + proxy_ip
            proxy = {'http': proxy_ip, 'https': proxy_ip}
        else:
            proxy = None
        return proxy

    # 请求url
    def get_site(self, url, PAGE):
        url = "https://www.kuaidaili.com/free/inha/%s/" % str(PAGE)
        # 输出日志到控制端
        self.logger.dbuglog(url)
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url=url, headers=self.headers, proxies=self.proxy, verify=False, timeout=5)
        return url, response

    # 解析网站信息
    def wash_text(self, response):
        # 用于网页信息分析，处理
        all_info = 0
        return all_info

    # 快代理网站
    def test(self, response):
        # 防止此代码报异常,导致循环无法退出
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
            return all_info
        except Exception as e:
            return all_info

    # 快代理网站
    def KuaiDaiLi(self, url):
        """
        该网站超出范围的页面显示：Invalid Page
        """
        PAGE = 1  # 获取当前页
        CUR_ERR_COUNT = 1  # 当前url允许连续错误次数
        ALL_ERR_COUNT = 10  # 连续重连错误允许总次数
        del_count = ALL_ERR_COUNT  # 连续重连错误允许剩余次数

        while True:
            time.sleep(1)
            url, response = self.get_site(url, PAGE)
            try:
                # 当前url重连和连续url错误次数
                del_count = self.judge_status(url, CUR_ERR_COUNT, del_count, ALL_ERR_COUNT, proxy)
                # 判断连续访问url的重连次数为最大值，退出程序
                if del_count <= 0:
                    self.logger.skiplog(url + '   -----url退出程序，连续url访问次数错误超过最大值')
                    break

                # 清洗数据
                all_info = self.wash_text(response)

                # 判断是否为最后一页,如果是退出
                if all_info < 15:
                    self.logger.skiplog(url + '   -----该url为最后一页')
                    break

            except Exception as e:
                # 保存到日志并打印到控制端
                self.logger.errlog(url + '  -----%s' % str(e))
                sleep_time = random.randint(1, 20)
                time.sleep(sleep_time * 0.1)
            finally:
                PAGE += 1


# 过滤并获取可用代理
class Usable_proxy(Public):
    def __init__(self):
        conn = MongoClient()
        self.db = conn['oneday']
        self.my_set = self.db['filer_proxy']

    # 获取测试代理ip
    @property
    def get_proxy(self):
        # 从数据库中获取数据
        my_colletion = self.db['proxy']
        proxy_list = my_colletion.find()
        for val in proxy_list:
            yield val


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
        try:
            for val in self.get_proxy:
                judge = self.check(val['ip_port'])
                if judge:
                    # 保存到数据库
                    self.my_set.save(val)
        except Exception as e:
            pass

proxy = Proxy()
proxy.KuaiDaiLi()
