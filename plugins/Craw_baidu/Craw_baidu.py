from plugins.BasePlugin.BasePlugin import BasePlugin
from plugins.Craw_baidu import Craw1
from plugins.Craw_baidu import getxml
from PyQt5.QtCore import pyqtSignal
import os

class Craw_baidu(BasePlugin):
    trigger = pyqtSignal()
    CrawProcess = pyqtSignal(str)
    def __init__(self, state=None, text=None, args={}, filepath=None, propath=None):
        super().__init__(state)
        self.text=text
        self.name=None
        self.describe=None
        self.configPath=None
        self.filepath=filepath
        self.propath=propath
        self.loadFromConfig()
        self.args=args
        self.args['flag']=True
        self.p_keys = ['name', 'describe', 'configPath', 'text', 'filepath', 'propath']
        self.parameters = {}.fromkeys(self.p_keys)
        # self.loadFromConfig()
        self.bd = Craw1.Baidu(filepath=self.filepath)

    def loadFromConfig(self):
        #遍历找到xml配置信息文件'path'
        #获取爬虫name，爬虫描述、保存文件路径和属性文件路径
        configfilePath = os.getcwd() + '/' + 'plugins/' + self.__class__.__name__ + '/' + self.__class__.__name__ + '.xml'
        self.getxml = getxml.read_xml_info(configfilePath)
        configDate = self.getxml.getfull()
        # self.configPath=getxml.rxi.pathos
        self.configPath = configfilePath
        self.name = configDate['name']
        self.describe = configDate['describe']
        if self.filepath == None:
            self.filepath = configDate['filepath']
        if self.propath == None:
            # self.propath = configDate['propertypath']
            self.propath = configDate['filepath']
        if os.path.exists(self.filepath):
            if self.filepath.find('Craw_baidu_ori') > 0:
                pass
            else:
                if 'Craw_baidu_ori' in os.listdir(self.filepath):
                    self.filepath=self.filepath+'Craw_baidu_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_baidu_ori'
                else:
                    os.makedirs(self.filepath+'Craw_baidu_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_baidu_ori')
                    self.filepath=self.filepath+'Craw_baidu_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_baidu_ori'
    def run(self):
        urls=[]
        urls = self.bd.geturls()
        for url in urls:
            if (int(self.bd.num) < int(self.getxml.getcount())) and self.args['flag']:
                self.bd.getdetail(url)
                print("正在爬取第" + str(self.bd.num) + "篇：" + self.bd.title)
                self.CrawProcess.emit(str("正在爬取第" + str(self.bd.num) + "篇：" + self.bd.title))
            else:
                break

        self.propath = os.path.abspath(os.path.join(self.filepath, ".."))
        self.bd.workbook.save(self.propath+'/Craw_baidu文献属性.xls')
        self.CrawProcess.emit('爬取完成')
        self.args['flag']=False

    def stop(self):
        self.args['flag'] = False
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
#     cb = Craw_baidu()
#     cb.getParameters()
#     t = threading.Thread(target=cb.run)
#     t.start()  # 开始爬取
#     time.sleep(20)
#     cb.stop()  # 停止爬取
#     t.join()