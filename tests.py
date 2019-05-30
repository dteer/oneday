import json
import re
import requests
proxies={'http':'121.61.3.243:9999','https':'121.61.3.243:9999'}
response = requests.get(url='http://baidu.com',proxies=proxies)
print(response.text)