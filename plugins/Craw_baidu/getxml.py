from xml.dom.minidom import parse


class read_xml_info:
    def __init__(self,file):
        # self.pathos=os.getcwd()+'/plugins/Craw_baidu/Craw_baidu.xml'
        self.file = file
        # self.pathos = os.getcwd().replace('\\', '/') + "/Craw_baidu.xml"
        # 读取配置文件路径
        self.dom = parse(self.file)
        # self.dom = parse(r'E:\Pythonworkspace\bdjs_crawl2\crawler.xml')
        # 获取文件元素对象
        self.content = self.dom.documentElement

    def isNone(self, obj1):
        if obj1 is None:
            return True
        else:
            return False

    def getcount(self):
        # dom = parse(self.file)
        # 读取配置文件中Condition数据
        condition_list = self.content.getElementsByTagName("Condition")
        # 获取DownloadCounts
        count_list = condition_list[0].getElementsByTagName("DownloadCounts")
        # 读值
        count = count_list[0].childNodes[0].data
        # print(count)
        return count

    def getfilepath(self):
        # dom = parse(self.file)
        FilePath_list = self.dom.getElementsByTagName("FilePath")
        fp = FilePath_list[0].firstChild.data
        # print(fp)
        return fp

    # def getpropertypath(self):
    #     # dom = parse(self.file)
    #     PropertyPath_list = self.dom.getElementsByTagName("PropertyPath")
    #     pp = PropertyPath_list[0].firstChild.data
    #     # print(fp)
    #     return pp

    def getfull(self):
        # dom = parse(self.file)
        Conditions = {}
        name = self.dom.getElementsByTagName('Name')
        Describe = self.dom.getElementsByTagName('Describe')
        Motifs = self.dom.getElementsByTagName('Motif')
        Keywords = self.dom.getElementsByTagName('Keyword')
        Relations = self.dom.getElementsByTagName('Relation')
        Magazines = self.dom.getElementsByTagName('Magazine')
        Publishdate_froms = self.dom.getElementsByTagName('Publishdate_from')
        Publishdate_tos = self.dom.getElementsByTagName('Publishdate_to')
        DownloadCounts = self.dom.getElementsByTagName('DownloadCounts')
        FilePath = self.dom.getElementsByTagName('FilePath')
        # PropertyPath = self.dom.getElementsByTagName('PropertyPath')

        Conditions['name']=" " if self.isNone(name[0].firstChild) else name[0].firstChild.data
        Conditions['describe']=" " if self.isNone(Describe[0].firstChild) else Describe[0].firstChild.data
        Conditions['motif']=" " if self.isNone(Motifs[0].firstChild) else Motifs[0].firstChild.data
        Conditions['keyword']=" " if self.isNone(Keywords[0].firstChild) else Keywords[0].firstChild.data
        Conditions['relation']=" " if self.isNone(Relations[0].firstChild) else Relations[0].firstChild.data
        Conditions['magazine']=" " if self.isNone(Magazines[0].firstChild) else Magazines[0].firstChild.data
        Conditions['from']=" " if self.isNone(Publishdate_froms[0].firstChild) else Publishdate_froms[0].firstChild.data
        Conditions['to']=" " if self.isNone(Publishdate_tos[0].firstChild) else Publishdate_tos[0].firstChild.data
        Conditions['count']=" " if self.isNone(DownloadCounts[0].firstChild) else DownloadCounts[0].firstChild.data
        Conditions['filepath']=" " if self.isNone(FilePath[0].firstChild) else FilePath[0].firstChild.data
        # Conditions['propertypath']=" " if self.isNone(PropertyPath[0].firstChild) else PropertyPath[0].firstChild.data
        return Conditions

# 实例化
# pathos = os.getcwd()
# print(pathos)
# rxi = read_xml_info()
# rxi.getcount()
# rxi.getfilepath()