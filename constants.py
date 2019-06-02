#已解析的网站
site_name = {
'kuaidaili':{'start':'https://www.kuaidaili.com/free/inha/','end':''}
}

#数据库信息修改

#模板:mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
conn_db = 'mongodb://127.0.0.1:27017'
proxy_db = 'oneday'                  #存储的数据库名
proxy_colletion = 'proxy'           #存储爬取的ip,proxy_db中的表名
filer_colletion = 'filer_proxy'     #清洗后的ip,proxy_db中的表名