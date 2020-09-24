#coding=utf-8
import xml.dom.minidom
class getXml:
    def __init__(self,file):
        self.file=file
    def isNone(self,obj1):
        if obj1 is None:
            return True
        else:
            return False

    def getCount(self):
        dom = xml.dom.minidom.parse(self.file)
        DownloadCounts=dom.getElementsByTagName('DownloadCounts')
        if self.isNone(DownloadCounts[0].firstChild):
            assert 1
        else:
            return DownloadCounts[0].firstChild.data

    '''获取导入文件配置信息'''
    def getDestination(self):
        dom = xml.dom.minidom.parse(self.file)
        IP = dom.getElementsByTagName('IP')
        Port = dom.getElementsByTagName('Port')
        serviceName = dom.getElementsByTagName('serviceName')
        userName = dom.getElementsByTagName('userName')
        passWord = dom.getElementsByTagName('password')
        Path = dom.getElementsByTagName('FilePath')
        # Path = dom.getElementsByTagName('Path')
        ##Type=dom.getElementsByTagName('Type')
        configs = {}
        if self.isNone(Path[0].firstChild):
            assert 1
        else:
            ip = IP[0].firstChild.data
            port = Port[0].firstChild.data
            servicename = serviceName[0].firstChild.data
            username = userName[0].firstChild.data
            password = passWord[0].firstChild.data
            configs['ip'] = ip
            configs['port'] = port
            configs['servicename'] = servicename
            configs['username'] = username
            configs['password'] = password
            if Path[0].firstChild.data[-1]=="/":
                configs['path'] = Path[0].firstChild.data[0:len(Path[0].firstChild.data)-1]
            else:
                configs['path'] = Path[0].firstChild.data
            ##configs['type']=Type[0].firstChild.data
            return configs
    def getfull(self):
        dom = xml.dom.minidom.parse(self.file)
        Conditions = {}
        name = dom.getElementsByTagName('Name')
        Describe= dom.getElementsByTagName('Describe')
        Motifs = dom.getElementsByTagName('Motif')
        Keywords = dom.getElementsByTagName('Keyword')
        Relations = dom.getElementsByTagName('Relation')
        Magazines = dom.getElementsByTagName('Magazine')
        Publishdate_froms = dom.getElementsByTagName('Publishdate_from')
        Publishdate_tos = dom.getElementsByTagName('Publishdate_to')
        DownloadCounts = dom.getElementsByTagName('DownloadCounts')
        FilePath = dom.getElementsByTagName('FilePath')
        ##Type = dom.getElementsByTagName('Type')
        # PropertyPath = dom.getElementsByTagName('PropertyPath')

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
        ##Conditions['type']=" " if self.isNone(Type[0].firstChild) else Type[0].firstChild.data
        # Conditions['propertypath']=" " if self.isNone(PropertyPath[0].firstChild) else PropertyPath[0].firstChild.data
        return Conditions
    def getData(self):
        '''解析知网爬虫配置文件中爬取条件'''
        dom = xml.dom.minidom.parse(self.file)
        Conditions={}
        Motifs=dom.getElementsByTagName('Motif')
        Keywords=dom.getElementsByTagName('Keyword')
        Relations=dom.getElementsByTagName('Relation')
        Magazines=dom.getElementsByTagName('Magazine')
        Publishdate_froms=dom.getElementsByTagName('Publishdate_from')
        Publishdate_tos=dom.getElementsByTagName('Publishdate_to')
        i=0
        if self.isNone(Motifs[0].firstChild):
            if self.isNone(Keywords[0].firstChild):
                assert 1
            else:
                i+=1
                Conditions['txt_%s_sel'%i] = 'KY'
                Conditions['txt_%s_value1'%i] = Keywords[0].firstChild.data
                Conditions['txt_%s_relation'%i] = '#CNKI_AND'
                Conditions['txt_%s_special1'%i] = '='
        else:
            i += 1
            Conditions['txt_%s_sel'%i]='SU$%=|'
            Conditions['txt_%s_value1'%i]=Motifs[0].firstChild.data
            Conditions['txt_%s_relation' % i] = '#CNKI_AND'
            Conditions['txt_%s_special1' % i] = '='
            if self.isNone(Keywords[0].firstChild):
                assert 1
            else:
                i+=1
                Conditions['txt_%s_logical'%i] = Relations[0].firstChild.data
                Conditions['txt_%s_sel'%i] = 'KY'
                Conditions['txt_%s_value1'%i] = Keywords[0].firstChild.data
                Conditions['txt_%s_relation'%i] = '#CNKI_AND'
                Conditions['txt_%s_special1'%i] = '='

        if self.isNone(Magazines[0].firstChild):
            assert 1
        else:
            Conditions['magazine_value1']=Magazines[0].firstChild.data
            Conditions['magazine_special1']='%'
        if self.isNone(Publishdate_froms[0].firstChild):
            assert 1
        else:
            Conditions['publishdate_from']=Publishdate_froms[0].firstChild.data+"-01-01"
        if self.isNone(Publishdate_tos[0].firstChild):
            assert 1
        else:
            Conditions['publishdate_to']=Publishdate_tos[0].firstChild.data+"-12-31"
        return Conditions
