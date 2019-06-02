# oneday
一个包含富有生命的项目

[免费代理池](https://github.com/SpiderClub/haipproxy)
[scylla](https://github.com/imWildCat/scylla)

#从中获取的IP代理网址
[89免费代理](http://www.89ip.cn/tqdl.html?num=9999)\
[快代理](https://www.kuaidaili.com/free/inha/1/)：国内高匿代理\
[快代理](https://www.kuaidaili.com/free/intr/1/)：国内普通代理\
[西刺免费代理IP](https://www.xicidaili.com/nn/1/)：国内高匿代理\
[西刺免费代理IP](https://www.xicidaili.com/nt/1/)：国内透明代理\
[西刺免费代理IP](https://www.xicidaili.com/wn/1/)：HTTPS代理\
[西刺免费代理IP](https://www.xicidaili.com/wt/1/)：http代理\
[西刺免费代理IP](https://www.xicidaili.com/qq/1/)：socks代理


#数据库
在此项目中选取的数据库为mongodb
######数据库存储约束:
        {   '_id':md5(ip:port),
            'ip':127.0.0.1,
            'port':8080,
            'time':0.5,
            'type':https/http
            proxy : 'ip:port'
        }

#使用说明
1.  调用此模块注意点,当前没有配置解析网站时,
        需要自身测试,可加载函数 get_site并提供返回值
        需要自定义函数:def mydef
        并在run('mydef')进行调用
        
#优化方面
1.在缓慢/代价大的初始化过程(初始化数据库、图形等)中,可以考虑虚拟代理

