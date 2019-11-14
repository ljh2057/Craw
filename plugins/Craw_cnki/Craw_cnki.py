from plugins.BasePlugin.BasePlugin import BasePlugin
from plugins.Craw_cnki import Getxml
from plugins.Craw_cnki import main
import os
from PyQt5.QtCore import  pyqtSignal
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
        '''遍历找到xml配置信息文件path'''
        configfilePath=os.getcwd()+'/'+'plugins/'+self.__class__.__name__+'/'+self.__class__.__name__+'.xml'
        # configfilePath=os.getcwd()+'/'+self.__class__.__name__+'/'+'.xml'
        print(configfilePath)
        self.getxml =Getxml.getXml(configfilePath)
        configDate = self.getxml.getfull()
        self.configPath=configfilePath
        '''
        加载配置信息
        获取爬虫name，爬虫描述、保存文件路径和属性文件路径
        '''
        self.name=configDate['name']
        self.describe=configDate['describe']
        if self.filepath==None:
            self.filepath = configDate['filepath']
        if self.propath==None:
            self.propath = configDate['filepath']
        # if self.propath==None:
        #     self.propath = configDate['propertypath']
    def run(self):
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
        self.args["flag"] = False
        self.args["count"] = 0
        self.trigger.emit()

    def stop(self):
        self.args["flag"] = False
        self.trigger.emit()
    '''保存数据，判断Craw_cnki_ori是否存在当前路径，不存在时创建'''
    def saveData(self):
        if os.path.exists(self.filepath):
            if self.filepath.find('Craw_cnki_ori') > 0:
                savepath = self.filepath
            else:
                if 'Craw_cnki_ori' in os.listdir(self.filepath):
                    savepath=self.filepath+'Craw_cnki_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_cnki_ori'
                else:
                    os.makedirs(self.filepath+'Craw_cnki_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_cnki_ori')
                    savepath=self.filepath+'Craw_cnki_ori' if self.filepath[-1] == '/' else self.filepath + '/Craw_cnki_ori'
            count = self.getxml.getCount()
            search = main.SearchTools(count)
            propath=os.path.abspath(os.path.join(savepath, ".."))
            # print(propath+'/Craw_cnki文献属性.xls')
            if os.path.exists(propath+'/Craw_cnki文献属性.xls'):
                os.remove(propath+'/Craw_cnki文献属性.xls')
            shutil.move('data/CAJs/Craw_cnki文献属性.xls',propath)
            search.move_file('data/CAJs',savepath)
            print("文件已存到%s目录下"%savepath)
        else:
            print("文件目录不存在")

    def getParameters(self):
        self.parameters['name']=self.name
        self.parameters['describe']=self.describe
        self.parameters['configPath']=self.configPath
        self.parameters['state']=self.state
        self.parameters['text']=self.text
        self.parameters['filepath']=self.filepath
        self.parameters['propath']=self.propath
        return self.parameters

