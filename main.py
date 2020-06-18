import os
import importlib
from keyword import iskeyword

def call_plugin(p_name,method,state=None,text=None,filepath=None,propath=None):
    #package='plugins.'+p_name 根据路径引入对应的插件模块
    obj = importlib.import_module('.' + p_name, package='plugins.'+p_name)
    c = getattr(obj,p_name)
    obj = c(state,text,filepath,propath) # new class
    mtd = getattr(obj,method)
    return mtd()
def getAllPlugin(filepath):
    plg_ls=[]
    files=os.listdir(filepath)
    for f in files:
        #过滤_开头、关键字模块，且为文件夹
        if not f.startswith('_') and not iskeyword(f) and os.path.isdir(filepath+'/'+f):
            #判断插件主模块是否存在，即插件文件夹名.py文件是否存在
            if os.path.exists(filepath+'/'+f+'/'+f+'.py') and f!='BasePlugin':
                plg_ls.append(f)

    # print(plg_ls)
    # for f in files:
    #     if f.endswith('.py') and not f.startswith('_') and not iskeyword(f):
    #         # print(os.path.splitext(f)[0])
    #         plg_ls.append(os.path.splitext(f)[0])
    # plgs={}.fromkeys(plg_ls)
    # for plugin in plgs:
    #     # obj = __import__(plugin)  # import module (同级目录)
    #     #importlib.import_module导入一个模块。参数 name 指定了以绝对或相对导入方式导入什么模块 (比如要么像这样 pkg.mod 或者这样 ..mod)。如果参数 name 使用相对导入的方式来指定，那么那个参数 packages 必须设置为那个包名，这个包名作为解析这个包名的锚点 (比如 import_module('..mod', 'pkg.subpkg') 将会导入 pkg.mod)。
    #     obj =importlib.import_module('.'+plugin,package='plugins')
    #     c = getattr(obj, plugin)
    #     obj=c()
    #     r=re.compile('(?!__)')#匹配非__开头
    #     plgs[plugin]=list(filter(r.match, dir(obj)))#dir(obj)列出obj所有方法，返回list，python3中filter默认返回filter类
    # return plgs
    return plg_ls

#
# import requests
# from bs4 import BeautifulSoup
# from PIL import Image
# url = "http://kdoc.cnki.net/kdoc/download.aspx"
# headers={
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Upgrade-Insecure-Requests": "1",
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.3',
#     'Host': 'kdoc.cnki.net',
#     'Connection': 'keep-alive',
#     'Cache-Control': 'max-age=0',
# }
#
# refence_file = requests.get(url, headers=headers)
# querystring = {"filename":"WOaxkYhNUZCFUOCVXVxZ3QLlnZmhTZXdmVwImTEZTSylDWvNnZ2l0NHtkNZ5kSHVXOrcncW5kYZhmQ=0TWStSWIVja0YHawpnVrJVaGB1Z4cFcltyZFt2V54kd1sCesZGWnZlNzNmdygnU4lkWY9ENT5mNDJ","tablename":"CJFDAUTO"}
#
#
# # soup = BeautifulSoup(refence_file, 'lxml')
# htmls = refence_file.text
# soup = BeautifulSoup(htmls, 'lxml')
# print(soup.find_all(('img')))
# while(len(soup.find_all(text="安全验证"))>0):
#     validCodeSubSrc = soup.find_all('img')[0]['src']
#
#     img_url = 'http://kns.cnki.net' + validCodeSubSrc
#     image_res = requests.get(img_url, headers=headers)
#     with open('data/crack_code.jpeg', 'wb') as file:
#         file.write(image_res.content)
#     image = Image.open('data/crack_code.jpeg')
#     image.show()
#     code = input('出现验证码，请手动输入：')
#     payload = "vcode="+code
#     response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
#
#     # res = requests.post(url, headers=headers, data={"vcode":code})
#     # print(response.text)
#     htmls = response.text
#
#
#     soup = BeautifulSoup(htmls, 'lxml')
# print(htmls)
#



from PIL import Image

import requests

# img_url="http://kns.cnki.net/kdoc/request/ValidateCode.ashx"
# image_res = requests.get(img_url)
# with open('data/crack_code.jpeg', 'wb') as file:
#     file.write(image_res.content)
# image = Image.open('data/crack_code.jpeg')
# image.show()
# code = input('出现验证码，请手动输入：')
url = "http://kdoc.cnki.net/kdoc/download.aspx?filename=rgVbrRmRNhWQmd1NZRnTvdzdyZ3RVdHRItmS1sUczR3U0llMN12RvMkeaVkaJlFNFVEZwcXY5FmTndXYzEzQvljZ2IEcvNjaXRXcxZEexUldKpGUQ9WNkRVOuFTWslnYo5EZIV3TUdmVwEHRjdmW4o2cwsiMvJ2T&tablename=CAPJLAST&dflag=pdfdown"
# payload = 'vcode='+code
headers = {
  'Referer': 'http://kdoc.cnki.net/kdoc/download.aspx?filename=VbrRmRNhWQmd1NZRnTvdzdyZ3RVdHRItmS1sUczR3U0llMN12RvMkeaVkaJlFNFVEZwcXY5FmTndXY=0zaOBzdCRWOTlHa6NnYO1WcolWSzEEZtdXcpF1Qn5ENWJneqZ3cUdmVwEHRjdmW4o2cwsiMvJ2Trg&tablename=CJFDAUTO',
    'Cookie':'LID=WEEvREcwSlJHSldRa1FhcTdnTnhYQ21Nd01oWm93MjJUR3ZDZEFmYkliMD0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;'

}
s = requests.Session()

# headers.setdefault("Cookie",cookie)
response=s.get(url, headers=headers)
print(response.text)
with open('data/CAJs/test.pdf', 'wb') as file:
    file.write(response.content)



