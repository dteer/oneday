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
import traceback


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
        self.stime = 0.5
        self.logger = Logger('log')
        conn = MongoClient()
        db = conn['oneday']
        self.my_set = db['proxy']

    def repeat_load(self, url, Load_count, proxy=None):
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
                self.logger.dbuglog('该url重连第%s次' % CUR_COUNT)
                response = requests.get(url=url, headers=self.headers, proxies=proxy, verify=False, timeout=5)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    self.logger.dbuglog('url重连成功,重连成功次数为：%s' % CUR_COUNT)
                    return True, response  # 在此做了两个返回值
                else:
                    time.sleep(self.stime)
                    if CUR_COUNT >= Load_count:
                        self.logger.dbuglog('url退出重连，次数超过最大值：%s' % CUR_COUNT)
                        return False
                    else:
                        time.sleep(1)
                        CUR_COUNT += 1
            except Exception as e:
                if CUR_COUNT >= Load_count:
                    self.logger.dbuglog('url退出重连，次数超过最大值：%s' % CUR_COUNT)
                    return False
                CUR_COUNT += 1

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
            proxy = ''
        return proxy

    # 请求url
    def get_site(self, start_url, PAGE, end_url=''):
        # url = "https://www.kuaidaili.com/free/inha/%s/" % str(PAGE)
        if not start_url.endswith('/'):
            start_url = start_url + '/'
        if not end_url.startswith('/') and end_url != '':
            end_url = end_url + '/'

        url = start_url + str(PAGE) + end_url
        try:
            # 输出日志到控制端
            self.logger.dbuglog(url)
            requests.packages.urllib3.disable_warnings()
            response = requests.get(url=url, headers=self.headers, proxies=self.proxy, verify=False, timeout=5)
            response.encoding = response.apparent_encoding
            self.logger.dbuglog('成功访问该url')
            return url, response
        except Exception as e:
            self.logger.dbuglog('访问该url失败，开始重新连接')
            response = ''
            return url, response

    # 解析网站信息
    def wash_text(self, response,site=None):
        # 用于网页信息分析，处理
        if site is None:
            bool, all_info = getattr(self, 'kuaidaili')()
        else:
            bool, all_info = getattr(self, site)()
        return bool,all_info

    # 快代理网站
    def CPU_spider(self, start_url=None, end_url=None,site=None):
        """
        该网站超出范围的页面显示：Invalid Page
        """
        PAGE = 1  # 获取当前页
        CUR_ERR_COUNT = 3  # 当前url允许连续错误次数
        ALL_ERR_COUNT = 10  # 连续重连错误允许总次数
        del_count = ALL_ERR_COUNT  # 连续重连错误允许剩余次数

        while True:
            time.sleep(1)
            url, response = self.get_site(start_url, PAGE, end_url)
            try:
                # 当前url重连和连续url错误次数
                if response == '' or response.status_code != 200:
                    self.logger.dbuglog('该url连接失败,进行重连')
                    judge = self.repeat_load(url, CUR_ERR_COUNT, self.proxy)

                    # 判断是否需要跳到下一个url
                    if type(judge) is tuple:
                        response = judge[1]
                        del_count = ALL_ERR_COUNT
                    else:
                        # url连接失败,连续重连错误允许次数 -1
                        del_count -= 1
                        # 是否需要退出程序(访问连续url错误次数达到最大值)
                        if del_count <= 0:
                            self.logger.skiplog(url + '   -----url退出程序，连续url访问次数错误超过最大值:CPU_spider')
                            break

                        # 判断是否跳到下一个url
                        else:
                            raise Exception("该url无法到达")
                # 清洗数据
                bool,all_info = self.wash_text(response)
                #记录错误信息到日记表
                if  not bool:
                    self.logger.skiplog(url + '   -----该url清洗数据失败或存入数据库失败:CPU_spider')

                # 判断是否为最后一页,如果是退出
                if 1 <= all_info < 15:
                    self.logger.skiplog(url + '   -----该url为最后一页')
                    break

            except Exception as e:
                # traceback.print_exc()
                # 保存到日志并打印到控制端
                self.logger.errlog(url + '    函数CPU_spider异常  -----%s' % str(e))
                sleep_time = random.randint(1, 20)
                time.sleep(sleep_time * 0.1)
            finally:
                PAGE += 1

    #对外开放的url接口
    def run(self,start_url=None,end_url=None,site_name=None):
        if site_name is None:
            self.CPU_spider(start_url, end_url)
        else:
            self.CPU_spider(site_name)

    # --------------以下为代理网站的解析

    # 快代理网站
    def kuaidaili(self,response):
        """
        :param response:
        :return: 第一个返回值为清洗结果，第二个返回值为解析结果
        """
        # 防止此代码报异常,导致循环无法退出
        try:
            response_text = response.text
            html = etree.HTML(response_text)
            all_info = html.xpath("//div[@id='list']//tbody/tr")
            if type(all_info) is not list:
                all_info = [all_info]
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
            self.logger.dbuglog('清洗数据成功并存入数据库成功')
            return True,len(all_info)
        except Exception as e:
            self.logger.dbuglog('清洗数据失败或存入数据库失败')
            return False,len(all_info)


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
proxy.run('https://www.kuaidaili.com/free/inha/')
