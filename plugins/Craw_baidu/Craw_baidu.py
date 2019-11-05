from plugins.BasePlugin.BasePlugin import BasePlugin
class Craw_baidu(BasePlugin):
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
    def loadFromConfig(self):
        #遍历找到xml配置信息文件'path'
        self.configPath='path'
        #加载配置信息
        #获取爬虫name，爬虫描述、保存文件路径和属性文件路径
        self.name='百度军事爬虫'
        self.describe='百度军事爬虫描述'

    def start(self):
        #百度军事新闻爬取
        #更新state、text
        pass
    def stop(self):
        #结束爬取
        #更新state、text
        pass
    def func(self):
        #自定义扩展方法
        pass

    def getParameters(self):
        p_keys=['name','describe','configPath','state','text','filepath','propath']
        parameters={}.fromkeys(p_keys)
        parameters['name']=self.name
        parameters['describe']=self.describe
        parameters['configPath']=self.configPath
        parameters['state']=self.state
        parameters['text']=self.text
        parameters['filepath']=self.filepath
        parameters['propath']=self.propath
        # parameters['propath']='/Users/macbookair/Plugin_project/plugins/Craw_cnki/craw_data_property'
        return parameters


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