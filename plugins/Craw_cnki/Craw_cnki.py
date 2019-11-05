from plugins.BasePlugin.BasePlugin import BasePlugin
from plugins.Craw_cnki import Getxml
from plugins.Craw_cnki import main
import os
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import shutil

class Craw_cnki(BasePlugin):
    trigger = pyqtSignal()
    CrawProcess=pyqtSignal(str)
    def __init__(self, state=None, text=None,args={},filepath=None,propath=None):
        super().__init__(state)
        self.text=text
        self.name=None
        self.args =args
        self.describe=None
        self.configPath=None
        self.filepath=filepath
        self.propath=propath
        self.p_keys=['name','describe','configPath','state','text','filepath','propath']
        self.parameters={}.fromkeys(self.p_keys)
        self.loadFromConfig()

    def loadFromConfig(self):
        #遍历找到xml配置信息文件'path'
        configfilePath=os.getcwd()+'/'+'plugins/'+self.__class__.__name__+'/'+self.__class__.__name__+'.xml'
        # configfilePath=os.getcwd()+'/'+self.__class__.__name__+'/'+'.xml'
        print(configfilePath)
        self.getxml =Getxml.getXml(configfilePath)
        configDate = self.getxml.getfull()

        # print(configDate)

        self.configPath=configfilePath
        #加载配置信息
        #获取爬虫name，爬虫描述、保存文件路径和属性文件路径
        self.name=configDate['name']
        self.describe=configDate['describe']
        #filepath或propath为None时更新，否则不更新
        if self.filepath==None:
            self.filepath = configDate['filepath']
        if self.propath==None:
            self.propath = configDate['propertypath']
    def run(self):
        # 对知网论文进行多条件爬取
        # 更新state、text
        self.args["flag"] = True
        self.args["count"] = 0
        self.args["state"] = '正在爬取'
        self.args["text"] = self.text
        self.args["CrawProcess"]=self.CrawProcess

        getxml = Getxml.getXml(self.configPath)
        user_input = getxml.getData()
        count = int(getxml.getCount()) * 20
        search = main.SearchTools(count)
        try:
            search.search_reference(user_input, self.args)
        except OSError:
            pass
        print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
        # self.progress_text.set("爬取完毕，共运行：" + self.s2h(time.perf_counter()))
        self.args["flag"] = False
        # self.progressbar.after(2000, self.progress(count))
        # self.progressbar.update()
        self.args["count"] = 0
        self.trigger.emit()
    def start(self):
        #对知网论文进行多条件爬取
        #更新state、text
        self.args["flag"] = True
        self.args["count"] = 0
        self.args["state"] = '正在爬取'
        self.args["text"] =self.text

        getxml = Getxml.getXml(self.configPath)
        user_input = getxml.getData()
        count = int(getxml.getCount())*20
        search = main.SearchTools(count)
        try:
            search.search_reference(user_input,self.args)
        except OSError:
            pass
        print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
        # self.progress_text.set("爬取完毕，共运行：" + self.s2h(time.perf_counter()))
        self.args["flag"] = False
        # self.progressbar.after(2000, self.progress(count))
        # self.progressbar.update()
        self.args["count"] = 0
    def stop(self):
        self.args["flag"] = False
        self.trigger.emit()

        #结束爬取
        #更新state、text
        pass
    def saveData(self):
        if os.path.exists(self.filepath):
            savepath = self.filepath
            count = self.getxml.getCount()
            search = main.SearchTools(count)
            search.move_file('data/CAJs',savepath)
            # proPath = os.getcwd() + '/' + 'plugins/' + self.__class__.__name__ + '/'

            # shutil.copy(savepath+'/文献属性.xls',self.propath)
            shutil.copy2(savepath+'/文献属性.xls',self.propath)
            print("文件已存到%s目录下"%savepath)
        else:
            # self.label_notice_text.set("文件目录不存在")
            print("文件目录不存在")

    def func(self):
        #自定义扩展方法
        pass
    def getParameters(self):
        self.parameters['name']=self.name
        self.parameters['describe']=self.describe
        self.parameters['configPath']=self.configPath
        self.parameters['state']=self.state
        self.parameters['text']=self.text
        self.parameters['filepath']=self.filepath
        self.parameters['propath']=self.propath
        return self.parameters
# craw_cnki=Craw_cnki()
# craw_cnki.loadFromConfig()
# craw_cnki.start()
# from .BasePlugin import BasePlugin
# class Craw_cnki(BasePlugin):
#     def __init__(self,configPath，state,text):
#         super(Craw_cnki, self).__init__(configPath,state)
#
#         super.__init__(configPath,state)
#         BasePlugin.__init__(self,configPath,state)
#         self.text=text
#     def start(self):
#         #对知网论文进行多条件爬取
#         #更新state、text
#         pass
#     def stop(self):
#         #结束爬取
#         #更新state、text
#         pass
#     def func(self):
#         #自定义扩展方法
#         pass
#
# # class plugin1:
# #     def mod1(self):
# #         pass
# #
# #     def start(self):
# #         print("this is plugin1 function start")
# #     def pause(self):
# #         print("this is plugin1 function pause")
# #     def stop(self):
# #         print("this is plugin1 function stop")
#
# # class BasePlugin(object):
# #     def __init__(self,configPath):
# #         self.configPath=configPath
# #     def start(self):
# #         pass
# #     def stop(self):
# #         pass
# # class Craw_cnki(BasePlugin):
# #     def __init__(self,configPath):
# #         BasePlugin.__init__(self,configPath)
# #     def start(self):
# #         #对知网论文进行爬取
# #         pass
# #     def stop(self):
# #         #结束爬取
# #         pass
# #     def func(self):
# #         #自定义扩展方法
# #         pass