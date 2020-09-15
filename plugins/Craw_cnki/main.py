# -*- coding: UTF-8 -*-
import urllib
import json
import requests
import re
import time, os, shutil, logging
from .GetConfig import config
from .CrackVerifyCode import crack
from .GetPageDetail import page_detail
# 引入字节编码
from urllib.parse import quote
# 引入beautifulsoup
from bs4 import BeautifulSoup
import shutil
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options

from requests.cookies import RequestsCookieJar
from urllib.parse import quote_plus, urlencode
from http import cookiejar



HEADER = config.crawl_headers
# 获取cookie
BASIC_URL = 'https://kns.cnki.net/kns/brief/result.aspx'
# 利用post请求先行注册一次
SEARCH_HANDLE_URL = 'https://kns.cnki.net/kns/request/SearchHandler.ashx'
# 发送get请求获得文献资源
GET_PAGE_URL = 'https://kns.cnki.net/kns/brief/brief.aspx?pagename='
# 下载的基础链接
DOWNLOAD_URL = 'https://kdoc.cnki.net/kdoc/'
# 切换页面基础链接
CHANGE_PAGE_URL = 'https://kns.cnki.net/kns/brief/brief.aspx'


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

    def get_cookies(self):
        self.webdriver_path = "D:\\workspaces\\pythonworks\\webdriver\\chromedriver_win32\\chromedriver.exe"
        # options = webdriver.ChromeOptions()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path=self.webdriver_path, chrome_options=chrome_options)
        # driver = webdriver.Chrome(self.webdriver_path)
        driver.get("https://www.cnki.net/")
        driver.find_element_by_id("txt_SearchText").click()
        sleep(2)
        driver.find_element_by_id("txt_SearchText").send_keys("机器学习")
        sleep(1)
        element = driver.find_element_by_class_name("search-btn")
        webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
        driver.find_element_by_class_name("search-btn").click()
        sleep(1)
        coo = driver.get_cookies()
        cookies = {}
        self.ck = str()
        # 获取cookie中的name和value,转化成requests可以使用的形式
        for cookie in coo:
            cookies[cookie['name']] = cookie['value']
            self.ck = self.ck + cookie['name'] + '=' + cookie['value'] + ';'
            # print(cookie['name'] + '=' + cookie['value'] + ';')
        return self.ck

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
            'DbPrefix': 'CJFQ',
            'DbCatalog': '中国学术期刊网络出版总库',
            # 'ConfigFile': 'SCDB.xml',
            'ConfigFile': 'CJFQ.xml',
            'db_opt': 'CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD',  # 搜索类别（CNKI右侧的）
            'his': '0',
            '__': time.asctime(time.localtime()) + ' GMT+0800 (中国标准时间)'
        }
        # 将固定字段与自定义字段组合
        post_data = {**static_post_data, **ueser_input}

        try:
            self.get_cookies()
        except Exception as e:
            print(e)
            print("cookie获取失败")

        # 必须有第一次请求，否则会提示服务器没有用户
        first_post_res = self.session.post(
            SEARCH_HANDLE_URL, data=post_data, headers=HEADER)
        # get请求中需要传入第一个检索条件的值
        key_value = quote(ueser_input.get('txt_1_value1'))
        # print("first_post_res:",first_post_res.text)
        # print("key_value:",key_value)
        self.get_result_url = GET_PAGE_URL + first_post_res.text + '&t=1544249384932&keyValue=' + key_value + '&S=1&sorttype='
        # 检索结果的第一个页面
        second_get_res = self.session.get(self.get_result_url,headers=HEADER)
        # cookies = second_get_res.cookies
        # cookie = requests.utils.dict_from_cookiejar(cookies)
        # print(cookie)
        # print(second_get_res.text)
        # second_get_res = self.session.get(SEARCH_HANDLE_URL, data=post_data,headers=HEADER)
        change_page_pattern_compile = re.compile(
            r'.*?pagerTitleCell.*?<a href="(.*?)".*')
        try:
            self.change_page_url = re.search(change_page_pattern_compile,
                                             second_get_res.text).group(1)
            print(self.change_page_url)

            try:
                self.parse_page(
                    self.pre_parse_page(second_get_res.text), second_get_res.text,args)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
        #     pass
        # self.parse_page(
        #     self.pre_parse_page(second_get_res.text), second_get_res.text,args)



    def pre_parse_page(self, page_source):
        '''
        用户选择需要检索的页数
        '''
        reference_num_pattern_compile = re.compile(r'.*?找到&nbsp;(.*?)&nbsp;')
        reference_num = re.search(reference_num_pattern_compile,
                                  page_source).group(1)
        reference_num_int = int(reference_num.replace(',', ''))
        print('检索到' + reference_num + '条结果，全部下载大约需要' +
              self.s2h(reference_num_int * 5) + '。')
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
                    print("开始下载前%d页所有文件，预计用时%s" % (page, self.s2h(page * 20 * 5)))
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
                # with open(
                #         'data/ReferenceList.txt', 'a',
                #         encoding='utf-8') as file:
                #     file.write(td_text + ' ')
                # 寻找下载链接
                dl_url = td_info.find('a', attrs={'class': 'briefDl_D'})


                # 寻找详情链接
                dt_url = td_info.find('a', attrs={'class': 'fz14'})
                # 排除不是所需要的列
                if dt_url:
                    detail_url = dt_url.attrs['href']
                if dl_url:
                    # download_url = dl_url.attrs['href']+"&dflag=pdfdown"
                    download_url = dl_url.attrs['href']+"&dflag=cajdown"
                    # download_url = dl_url.attrs['href']
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
                            # with open('data/ReferenceList.txt', 'a', encoding='utf-8') as file:
                            #     file.write('\n')
                        else:
                            logging.error("无下载链接")
                    # time.sleep(0.5)
                else:
                    args["CrawProcess"].emit('爬取结束')
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
        print("url---------------", self.download_url)
        if len(self.download_url) > 40:
            args['count']+=1
            self.pg="正在下载第%s/%s篇文献"%(args['count'],str(self.select_download_num))
            self.info='节点1_正在下载: ' + single_refence_list[1] + '.caj'

            args["CrawProcess"].emit(str(self.pg+"\n"+self.info))
            # print(type(args["CrawProcess"]))


            name = single_refence_list[1]
            # name = single_refence_list[1] + '_' + single_refence_list[2]
            '''检查文件命名，防止网站资源有特殊字符本地无法保存'''
            file_pattern_compile = re.compile(r'[\\/:\*\?"<>\|]')
            name = re.sub(file_pattern_compile, '', name)
            # with open('data/Links.txt', 'a', encoding='utf-8') as file:
            #     file.write(self.download_url + '\n')
            # if config.crawl_isdownload ==1:
            if not os.path.isdir('data/CAJs'):
                os.mkdir(r'data/CAJs')
            # filename = self.docid+name+".pdf"
            filename = self.docid+name+".caj"
            try:
                if not os.path.isfile(os.path.join("data/CAJs/", filename)):
                    sess = requests.Session()
                    HEADER['Referer'] = self.download_url
                    # HEADER['Cookie'] = 'LID=WEEvREcwSlJHSldSdmVqelcxVTNETUwxSkpTdzNSelZPMGtUTTR3djg1QT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;'
                    # HEADER['Cookie'] = 'CurrSortFieldType=desc;CurrSortField=%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2f(%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2c%27TIME%27);c_m_LinID=LinID=WEEvREcwSlJHSldSdmVqelcxVTNETUwwTExCbEZsQXRxTzRsVnpSSVpvTT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=09/15/2020 15:04:56;cnkiUserKey=80843df4-4597-8109-17a3-f4f7642134c4;Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"NJ0023","ShowName":"%E6%B2%B3%E6%B5%B7%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"fC3r2l"};c_m_expire=2020-09-15 15:04:56;SID_kns8=123112;Ecp_session=1;ASP.NET_SessionId=cdwbc4sppmhjofebxlgpbbp4;SID_kns_new=kns123121;Ecp_ClientId=5200915144402179584;Ecp_notFirstLogin=fC3r2l;LID=WEEvREcwSlJHSldSdmVqelcxVTNETUwwTExCbEZsQXRxTzRsVnpSSVpvTT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;'
                    # HEADER['Cookie'] = 'c_m_LinID=LinID=WEEvREcwSlJHSldSdmVqM1BLUWdMWjVRTFY0MHlhNld6cXdxem9kRXpzcz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=09/15/2020 16:25:29;cnkiUserKey=700c6580-66f0-d89f-414c-c84f72dc52fa;c_m_expire=2020-09-15 16:25:29;SID_kns8=123106;ASP.NET_SessionId=qag4isl11jbdrt0mjunnyvjr;SID_kns_new=kns123117;Ecp_ClientId=1200915160502413634;Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"NJ0023","ShowName":"%E6%B2%B3%E6%B5%B7%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"rptZbY"};Ecp_notFirstLogin=rptZbY;LID=WEEvREcwSlJHSldSdmVqM1BLUWdMWjVRTFY0MHlhNld6cXdxem9kRXpzcz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;Ecp_session=1;'
                    HEADER['Cookie'] = self.ck
                    # HEADER['Cookie'] = 'LID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNhNzBDTkc0T2JDR3YwelNIc2FMMD0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;'
                    refence_file = sess.get(self.download_url, headers=HEADER)
                    with open('data/CAJs/' + filename, 'wb') as file:
                        file.write(refence_file.content)
                    # refence_file = requests.get(self.download_url,headers=HEADER)
                    # with open('data/CAJs/' + filename , 'wb') as file:
                    #     file.write(refence_file.content)

                    # print(self.download_url)

                    # refence_file =sess.get(self.download_url,headers=HEADER)

                    # htmls = refence_file.text
                    # soup = BeautifulSoup(htmls, 'lxml')
                    # print(soup.find_all(('img')))
                    # if len(soup.find_all('img'))>0:
                    #
                    #     validCodeSubSrc = soup.find_all('img')[0]['src']
                    #
                    #     code=crack.get_image2(validCodeSubSrc, self.session)
                    #
                    #     HEADER['Referer'] = self.download_url
                    #
                    #     payload = "vcode=" + code
                    #     ret = sess.post(self.download_url, data=payload)
                    #     print(ret)



            except Exception as e:
                logging.error(e)
                logging.error('下载出错')
            time.sleep(config.crawl_stepWaitTime)
    '''移动文件到指定路径'''
    def move_file(self,src_dir, target_dir):
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        for item in os.listdir(src_dir):
            src_name = os.path.join(src_dir, item)
            target_name = os.path.join(target_dir, item)
            shutil.move(src_name, target_name)

    def s2h(self,seconds):
        '''
        将秒数转为小时数
        '''
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return ("%02d小时%02d分钟%02d秒" % (h, m, s))


# Ecp_ClientId=1200824163400713266; RsPerPage=20; cnkiUserKey=3bc189b4-1612-5130-3b53-e91d7f426804; _pk_ref=%5B%22%22%2C%22%22%2C1599961800%2C%22https%3A%2F%2Fwww.cnki.net%2F%22%5D; LID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNiSkpvbExySllXaCs1MkpUR1NCST0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; Ecp_session=1; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"NJ0023","ShowName":"%E6%B2%B3%E6%B5%B7%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"5BEo2M"}; ASP.NET_SessionId=xer0y025pdahbeg1pdbooazq; SID_kns8=123110; c_m_LinID=LinID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNiSkpvbExySllXaCs1MkpUR1NCST0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=09/14/2020 10:08:51; c_m_expire=2020-09-14 10:08:51
# Ecp_ClientId=1200824163400713266; RsPerPage=20; cnkiUserKey=3bc189b4-1612-5130-3b53-e91d7f426804; _pk_ref=%5B%22%22%2C%22%22%2C1599961800%2C%22https%3A%2F%2Fwww.cnki.net%2F%22%5D; LID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNiSkpvbExySllXaCs1MkpUR1NCST0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; Ecp_session=1; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"NJ0023","ShowName":"%E6%B2%B3%E6%B5%B7%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"5BEo2M"}; ASP.NET_SessionId=xer0y025pdahbeg1pdbooazq; SID_kns8=123110; c_m_LinID=LinID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNiSkpvbExySllXaCs1MkpUR1NCST0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=09/14/2020 10:08:51; c_m_expire=2020-09-14 10:08:51
# Ecp_notFirstLogin=5BEo2M; Ecp_ClientId=1200824163400713266; RsPerPage=20; cnkiUserKey=3bc189b4-1612-5130-3b53-e91d7f426804; _pk_ref=%5B%22%22%2C%22%22%2C1599961800%2C%22https%3A%2F%2Fwww.cnki.net%2F%22%5D; LID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNiSkpvbExySllXaCs1MkpUR1NCST0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; Ecp_session=1; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"NJ0023","ShowName":"%E6%B2%B3%E6%B5%B7%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"5BEo2M"}; ASP.NET_SessionId=xer0y025pdahbeg1pdbooazq; SID_kns8=123110; CurrSortField=%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2f(%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2c%27TIME%27); CurrSortFieldType=desc; SID_kcms=124108; c_m_LinID=LinID=WEEvREcwSlJHSldSdmVqMDh6aS9uaHNiSkpvbExySllXaCs1MkpUR1NCST0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=09/14/2020 10:11:55; c_m_expire=2020-09-14 10:11:55
# https://kns.cnki.net/kcms/download.aspx?filename=w5WUJNFV5pmdrlTbJp3SaNXa09Gbr4GWLZGOLVkcotyYNBDVl9WVyRHTxFnVzRHSuV2LWxkei9mbyhVUwVmdNxUanZ0d1VHZYVUQpJzZYJ1QEdWekx2cwJ3dyFjcxEzQitGWNhnQzoGNptSaj9yaNJ0NDdGMCllU&tablename=CAPJLAST&dflag=cajdown
