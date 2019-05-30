import json
import re
import requests
def t():
    a,b= True,2
    return a,b
a= t()

if type(a) is tuple:
    c,d = a
    print(c,d)

t = (1,2,3,4)
