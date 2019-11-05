
import urllib
import requests
import re
import time, os, shutil, logging
from .UserInput import get_uesr_inpt
from .GetConfig import config
from .CrackVerifyCode import crack
from .GetPageDetail import page_detail
# 引入字节编码
from urllib.parse import quote
# 引入beautifulsoup
from bs4 import BeautifulSoup
import shutil
import xlrd
import traceback
from tkinter import *
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,QDesktopWidget, QFileDialog, QApplication,QPushButton)




HEADER = config.crawl_headers
# 获取cookie
BASIC_URL = 'http://kns.cnki.net/kns/brief/result.aspx'
# 利用post请求先行注册一次
SEARCH_HANDLE_URL = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
# 发送get请求获得文献资源
GET_PAGE_URL = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename='
# 下载的基础链接
DOWNLOAD_URL = 'http://kns.cnki.net/kns/'
# 切换页面基础链接
CHANGE_PAGE_URL = 'http://kns.cnki.net/kns/brief/brief.aspx'


class SearchTools(object):
    '''
    构建搜索类
    实现搜索方法
    '''

    def __init__(self,count):
        self.session = requests.Session()
        self.sheet_name = "CRA" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.index = 0
        self.cur_page_num = 1
        # 保持会话
        self.session.get(BASIC_URL, headers=HEADER)
        self.count=count

    def search_reference(self, ueser_input,args):
        '''
        第一次发送post请求
        再一次发送get请求,这次请求没有写文献等东西
        两次请求来获得文献列表
        '''
        if os.path.isdir('data'):
            # 递归删除文件
            shutil.rmtree('data')
            # 创建一个空的
        os.mkdir('data')
        '''DbPrefix 为CFLS时 仅下载中文，SCDB 下载中英文（英文无下载链接）'''
        static_post_data = {
            'action': '',
            'NaviCode': '*',
            'ua': '1.21',
            'isinEn': '1',
            'PageName': 'ASP.brief_result_aspx',
            'DbPrefix': 'CFLS',
            'DbCatalog': '中国学术期刊网络出版总库',
            'ConfigFile': 'SCDB.xml',
            'db_opt': 'CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD',  # 搜索类别（CNKI右侧的）
            'his': '0',
            '__': time.asctime(time.localtime()) + ' GMT+0800 (中国标准时间)'
        }
        # 将固定字段与自定义字段组合
        post_data = {**static_post_data, **ueser_input}
        # 必须有第一次请求，否则会提示服务器没有用户
        first_post_res = self.session.post(
            SEARCH_HANDLE_URL, data=post_data, headers=HEADER)
        # get请求中需要传入第一个检索条件的值
        key_value = quote(ueser_input.get('txt_1_value1'))
        self.get_result_url = GET_PAGE_URL + first_post_res.text + '&t=1544249384932&keyValue=' + key_value + '&S=1&sorttype='
        # 检索结果的第一个页面
        second_get_res = self.session.get(self.get_result_url,headers=HEADER)
        # second_get_res = self.session.get(SEARCH_HANDLE_URL, data=post_data,headers=HEADER)
        change_page_pattern_compile = re.compile(
            r'.*?pagerTitleCell.*?<a href="(.*?)".*')
        try:
            self.change_page_url = re.search(change_page_pattern_compile,
                                             second_get_res.text).group(1)
            try:
                self.parse_page(
                    self.pre_parse_page(second_get_res.text), second_get_res.text,args)
            except OSError:
                pass
        except OSError:
            pass


    def pre_parse_page(self, page_source):
        '''
        用户选择需要检索的页数
        '''
        reference_num_pattern_compile = re.compile(r'.*?找到&nbsp;(.*?)&nbsp;')
        reference_num = re.search(reference_num_pattern_compile,
                                  page_source).group(1)
        reference_num_int = int(reference_num.replace(',', ''))
        print('检索到' + reference_num + '条结果，全部下载大约需要' +
              s2h(reference_num_int * 5) + '。')
        # is_all_download = input('是否要全部下载（y/n）?')
        is_all_download = 'n'
        # 将所有数量根据每页20计算多少页
        if is_all_download == 'y':
            page, i = divmod(reference_num_int, 20)
            if i != 0:
                page += 1
            return page
        else:
            count = self.count
            self.select_download_num = int(count)
            while True:
                if self.select_download_num > reference_num_int:
                    print('输入数量大于检索结果，请重新输入！')
                    self.select_download_num = int(input('请输入需要下载的数量（不满一页将下载整页）：'))
                else:
                    page, i = divmod(self.select_download_num, 20)
                    # 不满一页的下载一整页
                    if i != 0:
                        page += 1
                    print("开始下载前%d页所有文件，预计用时%s" % (page, s2h(page * 20 * 5)))
                    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
                    return page

    def parse_page(self, download_page_left, page_source,args):
        '''
        保存页面信息
        解析每一页的下载地址
        '''
        soup = BeautifulSoup(page_source, 'lxml')
        # 定位到内容表区域
        tr_table = soup.find(name='table', attrs={'class': 'GridTableContent'})
        # 处理验证码
        try:
            # 去除第一个tr标签（表头）
            tr_table.tr.extract()
        except Exception as e:
            logging.error('出现验证码')
            return self.parse_page(
                download_page_left,
                crack.get_image(self.get_result_url, self.session,
                                page_source),args)
        # 遍历每一行
        for index, tr_info in enumerate(tr_table.find_all(name='tr')):
            tr_text = ''
            download_url = ''
            detail_url = ''
            # 遍历每一列
            for index, td_info in enumerate(tr_info.find_all(name='td')):
                # 因为一列中的信息非常杂乱，此处进行二次拼接
                td_text = ''
                for string in td_info.stripped_strings:
                    td_text += string
                tr_text += td_text + ' '
                with open(
                        'data/ReferenceList.txt', 'a',
                        encoding='utf-8') as file:
                    file.write(td_text + ' ')
                # 寻找下载链接
                dl_url = td_info.find('a', attrs={'class': 'briefDl_D'})
                # 寻找详情链接
                dt_url = td_info.find('a', attrs={'class': 'fz14'})
                # 排除不是所需要的列
                if dt_url:
                    detail_url = dt_url.attrs['href']
                if dl_url:
                    download_url = dl_url.attrs['href']
            try:
                # 将每一篇文献的信息分组
                single_refence_list = tr_text.split(' ')
                if args["flag"] == True:
                    self.index += 1
                    self.docid = self.sheet_name + str(self.index).zfill(4)
                    self.download_refence(download_url, single_refence_list,args)
                    # 是否开启详情页数据抓取
                    if config.crawl_isdetail ==1:
                        time.sleep(config.crawl_stepWaitTime)
                        if len(self.download_url)>40:

                            page_detail.get_detail_page(self.session, self.get_result_url,
                                                        detail_url, single_refence_list,
                                                        self.download_url,self.docid)
                            with open('data/ReferenceList.txt', 'a', encoding='utf-8') as file:
                                file.write('\n')
                        else:
                            logging.error("无下载链接")
                    # time.sleep(0.5)
                else:
                    # args['show_progress'].insert(INSERT,"结束爬取\n")
                    # args['text']="结束爬取"
                    print("结束爬取，退出")
                    break
                    # exit()

            except OSError:
                pass
        # download_page_left为剩余等待遍历页面
        if download_page_left > 1:
            self.cur_page_num += 1
            self.get_another_page(download_page_left,args)

    def get_another_page(self, download_page_left,args):
        '''
        请求其他页面和请求第一个页面形式不同
        重新构造请求
        '''
        time.sleep(config.crawl_stepWaitTime)
        curpage_pattern_compile = re.compile(r'.*?curpage=(\d+).*?')
        self.get_result_url = CHANGE_PAGE_URL + re.sub(
            curpage_pattern_compile, '?curpage=' + str(self.cur_page_num),
            self.change_page_url)
        get_res = self.session.get(self.get_result_url, headers=HEADER)
        download_page_left -= 1
        self.parse_page(download_page_left, get_res.text,args)


    def download_refence(self,url, single_refence_list,args):
        '''
        拼接下载地址
        进行文献下载
        '''
        # 拼接下载地址
        self.download_url = DOWNLOAD_URL + re.sub(r'../', '', url)
        if len(self.download_url) > 40:
            args['count']+=1
            self.pg="正在下载第%s/%s篇文献"%(args['count'],str(self.select_download_num))
            self.info='节点1_正在下载: ' + single_refence_list[1] + '.caj'
            # try:
            #     # print(args['text'])
            #     # args['text'].setText('')
            # except OSError:
            #     pass
            args["CrawProcess"].emit(str(self.pg+"\n"+self.info))
            # args['text'].setText(self.pg+"\n"+self.info)
            # args['text'].setText(self.info+"\n")
            # print(args['text'].toPlainText())
            #解决线程执行，耗时久页面卡顿问题
            # QApplication.processEvents()

            # print(args['text'])

            name = single_refence_list[1]
            # name = single_refence_list[1] + '_' + single_refence_list[2]
            # 检查文件命名，防止网站资源有特殊字符本地无法保存
            file_pattern_compile = re.compile(r'[\\/:\*\?"<>\|]')
            name = re.sub(file_pattern_compile, '', name)
            with open('data/Links.txt', 'a', encoding='utf-8') as file:
                file.write(self.download_url + '\n')
            # 检查是否下载
            # if config.crawl_isdownload ==1:
            if not os.path.isdir('data/CAJs'):
                os.mkdir(r'data/CAJs')
            # refence_file = requests.get(self.download_url, headers=HEADER)
            # refence_file = urllib2.urlopen(self.download_url)
            # data = refence_file.read()
            # with open('data/CAJs/' + name + '.caj', 'wb') as file:
            filename=self.docid+name+".caj"
            try:
                if not os.path.isfile(os.path.join("data/CAJs/", filename)):
                    urllib.request.urlretrieve(self.download_url, os.path.join('data/CAJs/', filename))
                    # file.write(refence_file.content)
                    # file.write(data)
            except Exception as e:
                logging.error('下载出错')

            time.sleep(config.crawl_stepWaitTime)


    def move_file(self,src_dir, target_dir):
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        for item in os.listdir(src_dir):
            src_name = os.path.join(src_dir, item)
            target_name = os.path.join(target_dir, item)
            shutil.move(src_name, target_name)




def s2h(seconds):
    '''
    将秒数转为小时数
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return ("%02d小时%02d分钟%02d秒" % (h, m, s))






if __name__ == '__main__':
    # main()
    list1=['a.caj','b.docx','c.txt','d.xls','ff.caj','ss.pdf','qssa.doc','sas.jpg']
    list2=[]
    tag = "UP" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    for i, f in enumerate(list1):
        if os.path.splitext(f)[1] in {'.caj', '.pdf', '.txt', '.doc', '.docx'}:
            list2.append(tag +str(i).zfill(4) + f)
    # print(list2)
    # print(os.getcwd())
    # cur_dir="/Users/macbookair/cnki/文献属性.xlsx/"
    # # print(cur_dir[:len(cur_dir)-8])
    # # for f in list1:
    #     # print(cur_dir+f)
    # # book = xlrd.open_workbook(cur_dir)
    # # # sheet = book.sheet_by_index(len(book.sheets())-1)
    # # sheets = book.sheets()
    # # for sheet in sheets:
    # #     print(sheet.name)
    # print(cur_dir[-1])
    # print(cur_dir[0:len(cur_dir)-1])
    sss='2019-12-01'
    # import datetime
    # import datetime
    # # print(time.strftime("%Y-%m-%d %X",sss))
    # # print(sss.apply(lambda x: type(time.strptime(x, '%Y-%m-%d'))))
    # print(datetime.datetime.strptime(sss, '%Y-%m-%d'))
    ops=[]
    for i in range(20):
        a=("第%s个"%i,"第%s个"%(i*2),"第%s个"%(i*3))
        ops.append(a)

    list2=[('第0个', '第6个', '第10个')]
    # for l in list1:
    #     print(l,end="\n")
    # new=[]
    # for l2 in list2:
    #     temp=[item for item in ops if item[1]==l2]
    #     new.extend(temp)
    # print(new)
    # ls=[item for item in ops if item not in new]
    # # ls=list(set(ops)-set(new))
    # print(ls)
    # print(new)
    #
    # for l in list1:
        # print(l,end="\n")
    # print(list1,end="\n")
    # print(list2[0][-1])
    print(os.getcwd())
