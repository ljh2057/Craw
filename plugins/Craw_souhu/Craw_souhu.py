# -*- coding: utf-8 -*-
from plugins.BasePlugin.BasePlugin import BasePlugin
import os
import pandas as pd
import openpyxl
from datetime import datetime
from plugins.Craw_souhu import news_crawler
from plugins.Craw_souhu import preprocessing
from plugins.Craw_souhu import getxml
from PyQt5.QtCore import  pyqtSignal
import threading
import time


class Craw_souhu(BasePlugin):
    trigger = pyqtSignal()
    CrawProcess = pyqtSignal(str)
    def __init__(self, state=None, text=None, args={}, filepath=None, propath=None):
        super().__init__(state)
        self.text = text
        self.name = None
        self.describe = None
        self.configPath = None
        self.filepath = filepath
        self.propath = propath
        self.loadFromConfig()
        self.args = args
        self.args['flag'] = True
        self.args["CrawProcess"] = self.CrawProcess
        self.p_keys = ['name', 'describe', 'configPath', 'text', 'filepath', 'propath']
        self.parameters = {}.fromkeys(self.p_keys)
        self.loadFromConfig()
        self.sh = news_crawler.Souhu(filepath=self.filepath, args=self.args)
        # self.sh = news_crawler.Souhu()

    def loadFromConfig(self):
        #遍历找到xml配置信息文件'path'
        #获取爬虫name，爬虫描述、保存文件路径和属性文件路径

        configfilePath=os.getcwd() + '/' + 'plugins/' + self.__class__.__name__ + '/' + self.__class__.__name__ + '.xml'
        self.xml = getxml.read_xml_info(configfilePath)
        configDate = self.xml.getfull()
        self.configPath = configfilePath
        self.name = configDate['name']
        self.describe = configDate['describe']
        if self.filepath == None:
            self.filepath = configDate['filepath']
        if self.propath == None:
            # self.propath = configDate['propertypath']
            self.propath = configDate['filepath']
        if os.path.exists(self.filepath):
            if self.filepath.find('Craw_souhu_ori') > 0:
                pass
            else:
                if 'Craw_souhu_ori' in os.listdir(self.filepath):
                    self.filepath=self.filepath+'Craw_souhu_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_souhu_ori'
                else:
                    os.makedirs(self.filepath+'Craw_souhu_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_souhu_ori')
                    self.filepath=self.filepath+'Craw_souhu_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_souhu_ori'

    """
    sh = news_crawler.Souhu()


    t = getxml.rxi.getcount()
    t = int(t)

    # project_path = getxml.rxi.getfilepath()
    project_path = os.path.dirname(os.path.realpath(__file__))  # 获取项目路径
    print("project_path......." + project_path)
    news_path = os.path.join(project_path, 'news')  # 新闻数据存放目录路径
    print("news_path......." + news_path)
    if not os.path.exists(news_path):  # 创建news文件夹
        os.mkdir(news_path)

    sohu_news_df = sh.get_latest_news('sohu', top=t, show_content=True)

    sh.save_to_txt(sohu_news_df, news_path, top=t)
    # print(news_path)
    sh.save_news(sohu_news_df, os.path.join(news_path, 'sohu_latest_news.csv'))

    """
    def run(self):
        # self.sh.flag = True
        # self.args["state"] = '正在爬取'
        t = self.xml.getcount()
        t = int(t)
        # project_path = os.path.dirname(os.path.realpath(__file__))  # 获取项目路径
        # print("project_path......." + project_path)
        # news_path = os.path.join(project_path, 'news')  # 新闻数据存放目录路径
        news_path = self.filepath
        # print("news_path......." + news_path)
        if not os.path.exists(news_path):  # 创建news文件夹
            os.mkdir(news_path)
        # sohu_news_df = self.sh.get_latest_news('sohu', top=t, show_content=True)
        sohu_news_df = self.sh.get_latest_news('sohu', path=news_path, top=t, show_content=True)
        # self.sh.save_to_txt(sohu_news_df, news_path, top=t)
        # print(news_path)
        fp = os.path.join(news_path, 'Craw_souhu文献属性.xlsx')
        self.sh.save_news(sohu_news_df, fp)
        # wb = openpyxl.load_workbook(fp)
        # ws = wb.worksheets[0]

        self.CrawProcess.emit('爬取完成')
        # self.sh.flag = False
        # fp = os.path.join(news_path, 'sohu_latest_news.csv')
        # print("filepath......" + fp)
        # df = pd.read_csv(fp)
        # df = df.astype(str)
        # df.insert(2, 'hhhhhhh', '')


        # self.propath = os.path.abspath(os.path.join(self.filepath, ".."))
        # self.sh.workbook.save(self.propath + '/Craw_baidu文献属性.xls')
        # self.CrawProcess.emit('爬取完成')
        # self.args['flag'] = False

    def stop(self):
        self.sh.flag = False
        # self.args["state"] = '爬取结束'
        # self.args['flag'] = False
        # print("stop")
        self.trigger.emit()

    def getParameters(self):
        self.parameters['name'] = self.name
        self.parameters['describe'] = self.describe
        self.parameters['configPath'] = self.configPath
        self.parameters['text'] = self.text
        self.parameters['filepath'] = self.filepath
        self.parameters['propath'] = self.propath
        # print(self.parameters)
        return self.parameters

# if __name__ == '__main__':
#     cs = Craw_souhu()
#     t = threading.Thread(target=cs.run)
#     t.start()  # 开始爬取
#     time.sleep(3)
#     cs.stop()  # 停止爬取
#     t.join()
#     # cs.run()



'''
sohu_news_df = news_crawler.get_latest_news('sohu', top=t, show_content=True)

news_crawler.save_to_txt(sohu_news_df, news_path, top=t)
# print(news_path)
news_crawler.save_news(sohu_news_df, os.path.join(news_path, 'sohu_latest_news.csv'))
'''

# df = pd.read_csv(r'D:\QQfiles\Craw\plugins\Craw_souhu\news\sohu_latest_news.csv', encoding= 'gb2312')  # 读文件
# data = ['1','2','3','4','5']
# df['new'] = data
# df.to_csv(r'D:\QQfiles\Craw\plugins\Craw_souhu\news\sohu_latest_news.csv', mode = 'a', index = False)
# # # df = df.astype(str)  # 转换数据为str
# # # df.insert(2, 'new_col', 1)






# news_df = sohu_news_df
# news_df = preprocessing.data_filter(news_df)
# last_time = datetime.today().strftime('%Y-%m-%d %H:%M')  # format like '2018-04-06 23:59'
# # last_time ='2018-04-06 23:59'
# news_df = preprocessing.get_data(news_df, last_time=last_time, delta=1)
# news_df['content'] = news_df['content'].map(lambda x: preprocessing.clean_content(x))
#
# news_crawler.save_news(news_df, os.path.join(news_path, 'latest_news.csv'))
