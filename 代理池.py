# encoding: utf-8
import urllib

import random
import requests
import urllib.request
from lxml import etree
import threading

"""
1.从代理ip网站爬取IP地址及端口号并储存
2.验证ip是否能用
3.格式化ip地址
4.在requests中使用代理ip爬取网站
"""

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
}


# 测试网页
def getHTMLText(url, proxies):
    try:
        r = requests.get(url, proxies=proxies)
        r.raise_for_status()  # 不成功抛异常
    except:
        return "代理不可用"
    else:
        return r.text


# 获取所有代理ip
def get_ip_list(url):
    """
    获取代理网站上的所有ip并验证可用性，
    返回代理池：格式：[{'http':'http://ip:port','https':'http://ip:port'}]
    """
    ip_list = []
    # 获取所有IP，生成列表
    web_data = requests.get(url, headers=headers)
    html = etree.HTML(web_data.text)
    trs = html.xpath("//table[@id='ip_list']//tr[position()>1]")
    for tr in trs:
        ips = tr.xpath(".//td/text()")
        ip_port = ips[0] + ':' + ips[1]
        ip_list.append(ip_port)

    return ip_list


#测试代理可用性 返回格式：[{}]
def check_proxy(ip_list):
    url = 'https://baidu.com'
    proxy_list = []
    for ip in ip_list:
        try:
            proxy_host = {'http': 'http://%s' % ip, 'https': 'http://%s' % ip}
            res = requests.get(url, headers=headers, proxies=proxy_host, timeout=0.5)
        except Exception as e:
            ip_list.remove(ip)
            continue
        else:
            proxy_list.append(
                {
                    'http': 'http://%s' % ip,
                    'https': 'http://%s' % ip
                }
            )
    return proxy_list


# 格式的转换，ip:port ===》 [{'http':'ip:port'}]
def C_format(datalist):
    proxy_list = []
    for ip in datalist:
        proxy_list.append(
            {
                'http': 'http://%s' % ip,
                'https': 'http://%s' % ip,
            }
        )
    return proxy_list




if __name__ == '__main__':
    url = 'http://www.xicidaili.com/nn/'
    ip_list = get_ip_list(url)
    #格式转换
    # proxy = C_format(ip_list)

    #测试代理可用性
    proxy = check_proxy(ip_list)
    print(proxy)

    # 访问网站测试
    # test_url = "http://httpbin.org/ip"
    test_url = "https://ip.cn/"
    proxies = random.choice(proxy)
    print(proxies)
    html = requests.get(test_url,proxies=proxies)
