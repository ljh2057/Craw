import hdfs
import pymysql
# import cx_Oracle as cx
import xlrd
import xlwt
import os
import time
import shutil
import uuid
from PyQt5.QtCore import pyqtSignal,QThread

import globalVar
from MainPage import Window


class BlobDataTestor(QThread):
    trigger = pyqtSignal()
    CrawProcess=pyqtSignal(str)
    def __init__(self,configs):
        super(BlobDataTestor, self).__init__()
        self.configs=configs
        try:
            self.conn = pymysql.connect(host=configs['ip'], port=int(configs['port']),user=configs['username'], passwd=configs['password'], db=configs['servicename'])
            # self.conn = cx.connect(configs['username'], configs['password'],
            #                        configs['ip'] + ":" + configs['port'] + "/" + configs['servicename'])
        except:
            pass
    def __del__(self):
        try:
            self.conn.close()
        except:
            pass

    def closedb(self):
        self.conn.close()

    def teardown(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("Drop Table sss")
        except:
            pass
    def run(self):
        self.upload_pfile(self.configs['path'])
        self.trigger.emit()


    def stop(self):
        self.configs['flag'] = False
        self.trigger.emit()

    def getDataFrom(self,filename):
        book = xlrd.open_workbook(filename)
        sheet = book.sheet_by_index(len(book.sheets())-1)
        ops = []
        for r in range(1, sheet.nrows):
            filepath = sheet.cell(r,11).value
            b = open(filepath, "rb").read()
            origin = pymysql.Binary(b)
            fileUuid = str(uuid.uuid1()).replace("-", "")
            values = (fileUuid,sheet.cell(r, 0).value[3:], sheet.cell(r, 2).value, sheet.cell(r, 3).value,sheet.cell(r, 4).value,sheet.cell(r, 5).value,sheet.cell(r, 6).value,sheet.cell(r, 7).value,sheet.cell(r, 8).value,sheet.cell(r, 9).value,sheet.cell(r, 10).value,origin,"1010","ZH")
            ops.append(values)
        cursor = self.conn.cursor()
        for n in range(0, len(ops)):
            try:
                cursor.executemany(
                    'insert into DOCUMENTS (UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD,ABSTRACT,JOURNAL,PUB_DT,URL,SUFFIX,CONTENT_ORI,SOURCE_CODE,LANG)values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    ops[n:n + 1])
            except OSError:
                pass
        cursor.close()
        self.conn.commit()
    '''简单导入'''
    def upload_simple(self,directory):
        f_list=os.listdir(directory)
        f_list_doc=[]
        ops = []
        tag = "UP" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        ut = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

        for i,f in enumerate(f_list):
            if os.path.splitext(f)[1] in {'.caj','.pdf','.txt','.doc','.docx'}:
                f_list_doc.append(tag+str(i).zfill(4)+f)
        for f in f_list_doc:
            b = open(directory+"/"+f[20:], "rb").read()
            origin = pymysql.Binary(b)
            fileUuid = str(uuid.uuid1()).replace("-", "")
            values =(fileUuid,f[:15][2:],ut,os.path.splitext(f)[0],os.path.splitext(f)[1],origin,"1010","ZH")
            ops.append(values)
        cursor = self.conn.cursor()
        for n in range(0, len(ops)):
            self.CrawProcess.emit(str("正在导入%s\n" % (ops[n][3])))
            try:
                if self.configs['flag']==True:
                    cursor.executemany(
                        'insert into DOCUMENTS(UUID,CRA_DT,UPLD_DT,TITLE,SUFFIX,CONTENT_ORI,SOURCE_CODE,LANG)values (%s, %s, %s, %s, %s, %s, %s, %s)',
                        ops[n:n + 1])
                else:
                    exit()

            except Exception as e:
                print(e)
                # pass
        cursor.close()
        self.conn.commit()

    def upload_pfile(self,cur_dir):
        '''
           构建字典存储爬虫插件对应的属性文件、原文文件夹、txt文本文件夹信息
           键为插件名,值为属性文件位置、原文文件文件夹位置ori、txt文本文件夹位置txt组成的列表
           当ori或txt文件夹不存在时,使用None占位
        '''
        f_all_dict = {}
        for f in os.listdir(cur_dir):
            if f.find('文献属性.xls') > 0 or f.find('文献属性.xlsx') > 0:
                filepro = cur_dir + f if cur_dir[-1] == '/' else cur_dir + '/' + f
                filepath = cur_dir + f[:f.find('文献属性')] + '_ori/' if cur_dir[-1] == '/' else cur_dir + '/' + f[:f.find(
                    '文献属性')] + '_ori/'
                filetxt = cur_dir + f[:f.find('文献属性')] + '_txt/' if cur_dir[-1] == '/' else cur_dir + '/' + f[:f.find(
                    '文献属性')] + '_txt/'
                f_all_dict.setdefault(f[:f.find('文献属性')], []).append(filepro) if os.path.exists(
                    filepro) else f_all_dict.setdefault(f[:f.find('文献属性')], []).append(None)
                f_all_dict.setdefault(f[:f.find('文献属性')], []).append(filepath) if os.path.exists(
                    filepath) else f_all_dict.setdefault(f[:f.find('文献属性')], []).append(None)
                f_all_dict.setdefault(f[:f.find('文献属性')], []).append(filetxt) if os.path.exists(
                    filetxt) else f_all_dict.setdefault(f[:f.find('文献属性')], []).append(None)
        for f_key in f_all_dict.keys():
            if f_all_dict[f_key][0] is not None:
                book = xlrd.open_workbook(f_all_dict[f_key][0])
                sheet = book.sheet_by_index(0)
                ut = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                ops = []
                '''
                逐行读取excel中信息,当爬取标注为CRA开头时,不添加上传标志UPA信息
                '''
                for r in range(1, sheet.nrows):
                    if sheet.cell(r, 0).value[0:3]=="CRA":
                        # values = (sheet.cell(r, 0).value[3:], sheet.cell(r, 2).value, sheet.cell(r, 3).value,sheet.cell(r, 4).value,sheet.cell(r, 5).value,sheet.cell(r, 6).value,sheet.cell(r, 7).value,sheet.cell(r, 8).value,sheet.cell(r, 9).value,sheet.cell(r,10).value,ut)
                        values = (sheet.cell(r, 0).value[3:], sheet.cell(r, 3).value, sheet.cell(r, 4).value,sheet.cell(r, 5).value,sheet.cell(r, 2).value,sheet.cell(r, 7).value,sheet.cell(r, 8).value,sheet.cell(r, 9).value,sheet.cell(r, 10).value,ut,sheet.cell(r,6).value)
                        # print("6666666666666", values)
                        ops.append(values)
                    else:
                        tag = "UPA" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        values = (tag[3:], str(sheet.cell(r, 3).value),str(sheet.cell(r, 4).value),str(sheet.cell(r, 5).value), tag+str(r).zfill(4)+str(sheet.cell(r, 2).value),str(sheet.cell(r, 7).value),str(sheet.cell(r, 8).value),str(sheet.cell(r, 9).value),str(sheet.cell(r,10).value),ut,str(sheet.cell(r,6).value))
                        # print("555555555555", values)
                        ops.append(values)
                if f_all_dict[f_key][1] is not None:
                    f_list = os.listdir(f_all_dict[f_key][1])
                    f_list_doc=[]
                    '''找到原文文件路径下所有文档,存到f_list_doc中'''
                    for f in f_list:
                        if os.path.splitext(f)[1] in {'.caj','.pdf','.txt','.doc','.docx'}:
                            self.suffix = os.path.splitext(f)[1]
                            f_list_doc.append(f)
                    temp_list=[]
                    # print("f_list_doc", len(f_list_doc)) 40
                    for f in f_list_doc:
                        for item in ops:
                            # print("item", item[10][0:3])
                            if item[4][0:3] == 'CRA':
                                if item[4] == os.path.splitext(f)[0]:
                                    temp_list.append(item)
                            else:
                                if item[4][21:] == os.path.splitext(f)[0]:
                                    temp_list.append(item)
                    '''文件存在且与属性文件一一匹配的'''
                    save_file=[]
                    for file in temp_list:
                        fileUuid=(str(uuid.uuid1()).replace("-", ""),)
                        if file[4][0:3]=='CRA':
                            filepath = f_all_dict[f_key][1] + file[4]+ '.' + file[8]
                        else:
                            filepath=f_all_dict[f_key][1]+file[4][21:]+'.'+file[8]
                        self.upload_filepath = filepath
                        try:
                            b = open(filepath, "rb").read()
                            origin = (pymysql.Binary(b),)
                            newfile=fileUuid+("1010","ZH")+file+origin
                            save_file.append(newfile)
                        except OSError:
                            if file[4][0:3] == 'CRA':
                                print('未找到文件'%file[4])
                            else:
                                print('未找到文件' % file[4][21:])
                    cursor = self.conn.cursor()
                    for n in range(0, len(save_file)):
                        a = globalVar.get_st()
                        print(a)
                        if a == 1:
                            self.CrawProcess.emit(str("正在导入%s\n" % (save_file[n][7])))
                            try:
                                # self.hdfs_ip = "http://192.168.1.107:50070"
                                # self.inputpath = '/4516/upload'
                                # self.client = hdfs.Client(self.hdfs_ip)
                                if self.configs['flag'] == True:
                                    cursor.executemany(
                                        "insert into DOCUMENTS(UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD,ABSTRACT,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,CONTENT_ORI,SOURCE_CODE,LANG)values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s)",
                                        save_file[n:n+1])
                                    # sql = "insert into DOCUMENTS(UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,SOURCE_CODE,LANG,ABSTRACT,CONTENT_ORI)values(:1, to_date(:2,'yyyy-mm-dd hh24:mi:ss'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)"
                                    # sql = "insert into DOCUMENTS(UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,SOURCE_CODE,LANG,ABSTRACT)values(:1, to_date(:2,'yyyy-mm-dd hh24:mi:ss'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14)"
                                    # txt导入
                                    sql = "insert into DOCUMENTS(UUID,SOURCE_CODE,LANG,CRA_DT,AUTHOR,KYWRD,AURDEPT,TITLE,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,ABSTRACT,CONTENT_ORI)values(:1, :2, :3, to_date(:4,'yyyy-mm-dd hh24:mi:ss'), :5, :6, :7, :8, :9, to_date(:10,'yyyy-mm-dd hh24:mi:ss'), :11, :12, to_date(:13,'yyyy-mm-dd hh24:mi:ss'), :14,:15)"
                                    # pdf导入
                                    # sql = "insert into DOCUMENTS(UUID,SOURCE_CODE,LANG,CRA_DT,AUTHOR,KYWRD,AURDEPT,TITLE,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,ABSTRACT)values(:1, :2, :3, to_date(:4,'yyyy-mm-dd hh24:mi:ss'), :5, :6, :7, :8, :9, to_date(:10,'yyyy-mm-dd hh24:mi:ss'), :11, :12, to_date(:13,'yyyy-mm-dd hh24:mi:ss'), :14)"
                                    # sql = "insert into DOCUMENTS(UUID,SOURCE_CODE,LANG,CRA_DT,AUTHOR,ABSTRACT,AURDEPT,KYWRD,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,TITLE)values('ce017578ec0411ea91d6a85e45b3a491', '1010', 'ZH', to_date('20200830203320','yyyy-mm-dd hh24:mi:ss'), '龙视要闻', '', '', '', '', to_date('20200830203320','yyyy-mm-dd hh24:mi:ss'), 'http://baijiahao.baidu.com/s?id=1676355714433432996', 'txt', to_date('20200830203320','yyyy-mm-dd hh24:mi:ss'), 'CRA202008302033200001美国最机密武器五年来首次现身，莫斯科：敢挑衅就摧毁')"
                                    # sql = "insert into DOCUMENTS(UUID,SOURCE_CODE,LANG,CRA_DT,AUTHOR,ABSTRACT,AURDEPT,KYWRD,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,TITLE)values('fUiiiuid', '', '', '', '', '', '', '', '', '', '', '', '', '')"
                                    # sql = "insert into DOCUMENTS(UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD)values('fUuid', to_date('2020-06-29 00:00:00','yyyy-mm-dd hh24:mi:ss'), 'hhhhhhhh', 'jjjjjjjjj', 'ooooo', 'ppppppp')"
                                    # a = ('ce017578ec0411ea91d6a85e45b3a491', '1010', 'ZH', '20200830203320', '龙视要闻', '', '', '', '', '2020-08-29', 'http://baijiahao.baidu.com/s?id=1676355714433432996', 'txt', '20200901113956', 'CRA202008302033200001美国最机密武器五年来首次现身，莫斯科：敢挑衅就摧毁')
                                    # 上传到oracle
                                    cursor.executemany(sql,
                                    #     # "insert into DOCUMENTS(UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,SOURCE_CODE,LANG,ABSTRACT,CONTENT_ORI)values(:1, to_date(:2,'yyyy-mm-dd hh24:mi:ss'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)",
                                    #     # "insert into DOCUMENTS(UUID,CRA_DT,TITLE,AUTHOR,AURDEPT,KYWRD,ABSTRACT,JOURNAL,PUB_DT,URL,SUFFIX,UPLD_DT,CONTENT_ORI,SOURCE_CODE,LANG)values(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)",
                                    #     # "insert into DOCUMENTS(UUID,CRA_DT,TITLE)values(:1, :2, :3)",
                                    save_file[n:n+1])
                                    # str(save_file[n:n+1]).replace('[','').replace(']',''))
                                    # cursor.execute(sql)
                                    try:
                                        # 上传到hdfs
                                        t = self.upload_filepath.rindex('/')
                                        self.client.upload(self.inputpath, self.upload_filepath[0:t+1]+save_file[n][7]+self.suffix)
                                    except Exception as e:
                                        print("upload error!", e)
                                else:
                                    break
                            except Exception as e:
                                print("1111111", e)
                        else:
                            break
                    self.CrawProcess.emit("导入完成")
                    cursor.close()
                    self.conn.commit()
                if f_all_dict[f_key][2] is not None:
                    self.upload_txt(f_all_dict[f_key][2])

    '''导入txt文本'''
    def upload_txt(self, directory):
        f_list = os.listdir(directory)
        f_list_txt = []
        ops = []
        for i, f in enumerate(f_list):
            if os.path.splitext(f)[1] == '.txt':
                f_list_txt.append(f)
        for f in f_list_txt:
            b = open(directory + f, 'r',encoding="gbk").read()
            values = ''.join(b)
            ops.append((values, os.path.splitext(f)[0]))
        cursor = self.conn.cursor()
        for n in range(0, len(ops)):
            try:
                if self.configs['flag'] == True:
                    cursor.executemany(
                        'update DOCUMENTS set CONTENT_TXT=%s where title=%s ',
                        ops[n:n + 1])
                else:
                    exit()
            except Exception as e:
                print(e)
        cursor.close()
        self.conn.commit()


if __name__ == '__main__':
    from plugins.Craw_cnki import Getxml
    # getxml = Getxml.getXml('/Users/macbookair/Plugin_project/ImportFile/importer.xml')
    a = os.getcwd()+"\\importer.xml"
    print(a.replace('/',"\\"))
    # getxml = Getxml.getXml('D:\\workspaces\\pythonworks\\20200913new\\Craw\\importer.xml')
    getxml = Getxml.getXml(a.replace('/',"\\"))

    configs = getxml.getDestination()
    bt=BlobDataTestor(configs)

    # cur_dir='/Users/macbookair/Plugin_project/craw_datas'
    '''
    构建字典存储爬虫插件对应的属性文件、原文文件夹、txt文本文件夹信息
    键为插件名,值为属性文件位置、原文文件文件夹位置ori、txt文本文件夹位置txt组成的列表
    当ori或txt文件夹不存在时,使用None占位
    '''
    # f_all_dict={}
    # for f in os.listdir(cur_dir):
    #     if  f.find('文献属性.xls')>0 or f.find('文献属性.xlsx')>0:
    #         filepro=cur_dir+f if cur_dir[-1]=='/' else cur_dir+'/'+f
    #         filepath=cur_dir+f[:f.find('文献属性')]+'_ori/' if cur_dir[-1]=='/' else cur_dir+'/'+f[:f.find('文献属性')]+'_ori/'
    #         filetxt=cur_dir+f[:f.find('文献属性')]+'_txt/' if cur_dir[-1]=='/' else cur_dir+'/'+f[:f.find('文献属性')]+'_txt/'
    #         f_all_dict.setdefault(f[:f.find('文献属性')], []).append(filepro) if os.path.exists(filepro) else f_all_dict.setdefault(f[:f.find('文献属性')], []).append(None)
    #         f_all_dict.setdefault(f[:f.find('文献属性')], []).append(filepath) if os.path.exists(filepath) else f_all_dict.setdefault(f[:f.find('文献属性')], []).append(None)
    #         f_all_dict.setdefault(f[:f.find('文献属性')], []).append(filetxt) if os.path.exists(filetxt) else f_all_dict.setdefault(f[:f.find('文献属性')], []).append(None)

    # print(f_all_dict)

    bt.upload_pfile(configs['path'])
