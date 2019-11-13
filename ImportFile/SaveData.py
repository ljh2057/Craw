import pymysql
import xlrd
import xlwt
import os
import time
import shutil
from PyQt5.QtCore import pyqtSignal,QThread


class BlobDataTestor(QThread):
    trigger = pyqtSignal()
    CrawProcess=pyqtSignal(str)
    def __init__(self,configs):
        super(BlobDataTestor, self).__init__()
        self.configs=configs
        try:
            self.conn = pymysql.connect(host=configs['ip'], port=int(configs['port']),user=configs['username'], passwd=configs['password'], db=configs['servicename'])
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
    def stop(self):
        self.configs['flag'] = False
        self.trigger.emit()

    def getDataFrom(self,filename):
        book = xlrd.open_workbook(filename)
        sheet = book.sheet_by_index(len(book.sheets())-1)
        ops = []
        for r in range(1, sheet.nrows):
            filepath=sheet.cell(r,11).value
            b = open(filepath, "rb").read()
            origin=pymysql.Binary(b)
            values = (sheet.cell(r, 0).value, sheet.cell(r, 1).value, sheet.cell(r, 2).value, sheet.cell(r, 3).value,sheet.cell(r, 4).value,sheet.cell(r, 5).value,sheet.cell(r, 6).value,sheet.cell(r, 7).value,sheet.cell(r, 8).value,sheet.cell(r, 9).value,sheet.cell(r, 10).value,origin)
            ops.append(values)
        cursor = self.conn.cursor()
        print("#######",sheet.name)
        cursor.execute("insert into corpus_sign(CRID)values('%s')"%sheet.name)

        for n in range(0, len(ops)):
            print(ops[n:n + 1])
            try:

                cursor.executemany(
                    'insert into tb_download (CRID,DOCID,TITLE,AUTHOR,DEPART,KEYWORD,ABSTRACT,JOURNAL,PT,URL,SUFFIX,ORIGIN)values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    ops[n:n + 1])
            except OSError:
                pass
            # except:
            #     pass
        cursor.close()
        self.conn.commit()
    # '''导入txt文本'''
    # def upload_txt(self,directory):
    #     f_list=os.listdir(directory)
    #     f_list_txt=[]
    #     ops = []
    #     for i,f in enumerate(f_list):
    #         if os.path.splitext(f)[1] =='.txt':
    #             f_list_txt.append(f)
    #     for f in f_list_txt:
    #         # b = open(directory+"/"+f[20:], "rb").read()
    #         # b = open(directory+"/"+f, "r")
    #         b = open(directory+"/"+f,'r').read()
    #         values=''.join(b)
    #         # values=values.strip('\n')
    #         print(values)
    #         # origin = pymysql.Binary(b)
    #         # values =(f[:15],f[:20],os.path.splitext(f)[0],os.path.splitext(f)[1],origin)
    #         ops.append((values,os.path.splitext(f)[0]))
    #     cursor = self.conn.cursor()
    #
    #     for n in range(0, len(ops)):
    #         self.CrawProcess.emit(str("正在导入%s\n" % (ops[n][2])))
    #         try:
    #             if self.configs['flag']==True:
    #                 print(ops[n:n + 1])
    #                 cursor.executemany(
    #                     'update tb_download set txt=%s where title=%s ',
    #                     ops[n:n + 1])
    #             else:
    #                 exit()
    #
    #         except Exception as e:
    #             print(e)
    #             # pass
    #     cursor.close()
    #     self.conn.commit()
    '''简单导入'''
    def upload_simple(self,directory):
        f_list=os.listdir(directory)
        f_list_doc=[]
        ops = []
        tag = "UP" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        ut = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        for i,f in enumerate(f_list):
            if os.path.splitext(f)[1] in {'.caj','.pdf','.txt','.doc','.docx'}:
                f_list_doc.append(tag+str(i).zfill(4)+f)
        for f in f_list_doc:
            b = open(directory+"/"+f[20:], "rb").read()
            origin = pymysql.Binary(b)
            values =(f[:15],f[:20],ut,os.path.splitext(f)[0],os.path.splitext(f)[1],origin)
            ops.append(values)
        cursor = self.conn.cursor()
        cursor.execute("insert into corpus_sign(CRID)values('%s')"%tag)

        for n in range(0, len(ops)):
            self.CrawProcess.emit(str("正在导入%s\n" % (ops[n][3])))
            try:
                if self.configs['flag']==True:
                    cursor.executemany(
                        'insert into corpus(CRID,DOCID,UT,TITLE,SUFFIX,ORIGIN)values (%s,%s, %s, %s, %s, %s)',
                        ops[n:n + 1])
                else:
                    exit()

            except Exception as e:
                print(e)
                # pass
        cursor.close()
        self.conn.commit()

    # '''从属性文件导入'''
    # def upload_pfile(self,filename):
    #     if os.path.splitext(filename)[1]==".xlsx":
    #         cur_dir=filename[:len(filename)-9]
    #     else:
    #         cur_dir=filename[:len(filename)-8]
    #
    #     book = xlrd.open_workbook(filename)
    #     sheet = book.sheet_by_index(0)
    #     ut = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    #
    #
    #     ops = []
    #     for r in range(1, sheet.nrows):
    #         if sheet.cell(r, 0).value[0:3]=="CRA":
    #             values = (sheet.cell(r, 0).value, sheet.cell(r, 1).value, sheet.cell(r, 2).value, sheet.cell(r, 3).value,sheet.cell(r, 4).value,sheet.cell(r, 5).value,sheet.cell(r, 6).value,sheet.cell(r, 7).value,sheet.cell(r, 8).value,sheet.cell(r, 9).value,sheet.cell(r,10).value,ut)
    #             ops.append(values)
    #         else:
    #             tag = "UPA" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    #             values = (tag, tag+str(r).zfill(4), tag+str(r).zfill(4)+str(sheet.cell(r, 2).value), str(sheet.cell(r, 3).value),str(sheet.cell(r, 4).value),str(sheet.cell(r, 5).value),str(sheet.cell(r, 6).value),str(sheet.cell(r, 7).value),str(sheet.cell(r, 8).value),str(sheet.cell(r, 9).value),str(sheet.cell(r,10).value),ut)
    #             ops.append(values)
    #     print(ops)
    #
    #     f_list = os.listdir(cur_dir)
    #     f_list_doc=[]
    #
    #     for f in f_list:
    #         if os.path.splitext(f)[1] in {'.caj','.pdf','.txt','.doc','.docx'}:
    #             f_list_doc.append(f)
    #
    #     temp_list=[]
    #     temp_list2=[]
    #     for f in f_list_doc:
    #         for item in ops:
    #             if item[2][0:3] == 'CRA':
    #                 if item[2] == os.path.splitext(f)[0]:
    #                     temp_list.append(item)
    #                     temp_list2.append(f)
    #             else:
    #                 if item[2][21:] == os.path.splitext(f)[0]:
    #                     temp_list.append(item)
    #                     temp_list2.append(f)
    #         # temp = [item for item in ops if item[2] == os.path.splitext(f)[0]]
    #     f_list_doc=list(set(f_list_doc)-set(temp_list2))
    #     # left_list = [item for item in f_list_doc if item not in temp_list]
    #     save_file=[]
    #     for file in temp_list:
    #         if file[2][0:3]=='CRA':
    #             filepath = cur_dir + file[2]+ '.' + file[10]
    #         else:
    #             filepath=cur_dir+file[2][21:]+'.'+file[10]
    #         try:
    #             b = open(filepath, "rb").read()
    #             origin = (pymysql.Binary(b),)
    #             newfile=file+origin
    #             save_file.append(newfile)
    #         except OSError:
    #
    #             if file[2][0:3] == 'CRA':
    #                 print('未找到文件'%file[2])
    #
    #                 # tk.messagebox.showinfo(title='提示', message=)
    #             else:
    #                 print('未找到文件' % file[2][21:])
    #                 # tk.messagebox.showinfo(title='提示', message='未找到文件'%file[2][17:])
    #
    #
    #     cursor = self.conn.cursor()
    #     if len(save_file)>0:
    #         try:
    #             if self.configs['flag']==True:
    #                 cursor.execute("insert into corpus_sign(CRID)values('%s')"%save_file[0][0])
    #         except Exception as e:
    #             print(e)
    #     for n in range(0, len(save_file)):
    #         self.CrawProcess.emit(str("正在导入%s\n" % (save_file[n][2])))
    #         try:
    #             cursor.executemany(
    #                 'insert into corpus (CRID,DOCID,TITLE,AUTHOR,DEPART,KEYWORD,ABSTRACT,JOURNAL,PT,URL,SUFFIX,ORIGIN,UT)values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)',
    #                 save_file[n:n+1])
    #         except Exception as e:
    #             print(e)
    #     cursor.close()
    #     self.conn.commit()
    #
    #
    #     if len(f_list_doc)>0:
    #         file_left_path=cur_dir+"无属性文献列表.xls"
    #         f_x=xlwt.Workbook()
    #         sheet=f_x.add_sheet('sheet1',cell_overwrite_ok=True)
    #
    #         flag=False
    #
    #         temp_file=cur_dir+'tempfile'
    #
    #         if not os.path.exists(temp_file):
    #             flag=True
    #             os.mkdir(temp_file)
    #
    #         i=0
    #         for ff in f_list_doc:
    #             src_name = os.path.join(cur_dir, ff)
    #             target_name = os.path.join(temp_file, ff)
    #             shutil.move(src_name, target_name)
    #             sheet.write(i,0,os.path.splitext(ff)[0])
    #             sheet.write(i,1,os.path.splitext(ff)[1])
    #             i+=1
    #         f_x.save(file_left_path)
    #         if flag:
    #             self.upload_simple(temp_file)
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
                ut = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                ops = []
                '''
                逐行读取excel中信息,当爬取标注为CRA开头时,不添加上传标志UPA信息
                '''
                for r in range(1, sheet.nrows):
                    if sheet.cell(r, 0).value[0:3]=="CRA":
                        values = (sheet.cell(r, 0).value, sheet.cell(r, 1).value, sheet.cell(r, 2).value, sheet.cell(r, 3).value,sheet.cell(r, 4).value,sheet.cell(r, 5).value,sheet.cell(r, 6).value,sheet.cell(r, 7).value,sheet.cell(r, 8).value,sheet.cell(r, 9).value,sheet.cell(r,10).value,ut)
                        ops.append(values)
                    else:
                        tag = "UPA" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        values = (tag, tag+str(r).zfill(4), tag+str(r).zfill(4)+str(sheet.cell(r, 2).value), str(sheet.cell(r, 3).value),str(sheet.cell(r, 4).value),str(sheet.cell(r, 5).value),str(sheet.cell(r, 6).value),str(sheet.cell(r, 7).value),str(sheet.cell(r, 8).value),str(sheet.cell(r, 9).value),str(sheet.cell(r,10).value),ut)
                        ops.append(values)
                print(ops)
                if f_all_dict[f_key][1] is not None:
                    f_list = os.listdir(f_all_dict[f_key][1])
                    f_list_doc=[]
                    '''找到原文文件路径下所有文档,存到f_list_doc中'''
                    for f in f_list:
                        if os.path.splitext(f)[1] in {'.caj','.pdf','.txt','.doc','.docx'}:
                            f_list_doc.append(f)

                    temp_list=[]
                    for f in f_list_doc:
                        for item in ops:
                            if item[2][0:3] == 'CRA':
                                if item[2] == os.path.splitext(f)[0]:
                                    temp_list.append(item)
                            else:
                                if item[2][21:] == os.path.splitext(f)[0]:
                                    temp_list.append(item)
                    '''文件存在且与属性文件一一匹配的'''
                    save_file=[]
                    for file in temp_list:
                        if file[2][0:3]=='CRA':
                            filepath = f_all_dict[f_key][1] + file[2]+ '.' + file[10]
                        else:
                            filepath=f_all_dict[f_key][1]+file[2][21:]+'.'+file[10]
                        try:
                            b = open(filepath, "rb").read()
                            origin = (pymysql.Binary(b),)
                            newfile=file+origin
                            save_file.append(newfile)
                        except OSError:

                            if file[2][0:3] == 'CRA':
                                print('未找到文件'%file[2])
                            else:
                                print('未找到文件' % file[2][21:])
                    cursor = self.conn.cursor()
                    if len(save_file)>0:
                        try:
                            if self.configs['flag']==True:
                                cursor.execute("insert into corpus_sign(CRID)values('%s')"%save_file[0][0])
                        except Exception as e:
                            print(e)
                    for n in range(0, len(save_file)):
                        self.CrawProcess.emit(str("正在导入%s\n" % (save_file[n][2])))
                        try:
                            if self.configs['flag'] == True:
                                cursor.executemany(
                                    "insert into corpus(CRID,DOCID,TITLE,AUTHOR,DEPART,KEYWORD,ABSTRACT,JOURNAL,PT,URL,SUFFIX,UT,ORIGIN)values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)",
                                    save_file[n:n+1])
                            else:
                                break
                        except Exception as e:
                            print(e)
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
            b = open(directory + "/" + f, 'r').read()
            values = ''.join(b)
            print(values)
            ops.append((values, os.path.splitext(f)[0]))
        cursor = self.conn.cursor()
        for n in range(0, len(ops)):
            # self.CrawProcess.emit(str("正在导入%s\n" % (ops[n][2])))
            try:
                if self.configs['flag'] == True:
                    print(ops[n:n + 1])
                    cursor.executemany(
                        'update corpus set txt=%s where title=%s ',
                        ops[n:n + 1])
                else:
                    exit()
            except Exception as e:
                print(e)
                # pass
        cursor.close()
        self.conn.commit()


if __name__ == '__main__':
    from plugins.Craw_cnki import Getxml
    getxml = Getxml.getXml('/Users/macbookair/Plugin_project/ImportFile/importer.xml')
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
