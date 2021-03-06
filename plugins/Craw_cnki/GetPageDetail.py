import xlwt
from bs4 import BeautifulSoup
import re
import math,random
from .GetConfig import config
import time
import os

HEADER = config.crawl_headers


class PageDetail(object):
    def __init__(self):
        # count用于计数excel行
        self.sheet_name = "CRA" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.excel = xlwt.Workbook(encoding='utf8')
        self.sheet = self.excel.add_sheet(self.sheet_name, True)
        self.set_style()
        self.sheet.write(0, 0, '标志',self.basic_style)
        self.sheet.write(0, 1, '序号',self.basic_style)
        self.sheet.write(0, 2, '题名',self.basic_style)
        self.sheet.write(0, 3, '作者',self.basic_style)
        self.sheet.write(0, 4, '单位',self.basic_style)
        self.sheet.write(0, 5, '关键字',self.basic_style)
        self.sheet.write(0, 6, '摘要',self.basic_style)
        self.sheet.write(0, 7, '来源',self.basic_style)
        self.sheet.write(0, 8, '发表时间',self.basic_style)
        self.sheet.write(0, 9, '下载地址',self.basic_style)
        self.sheet.write(0, 10, '后缀',self.basic_style)
        # self.sheet.write(0, 11, '源文件位置',self.basic_style)
        self.docid=""
        self.index=0

        # 生成userKey,服务器不做验证
        self.cnkiUserKey=self.set_new_guid()

    def get_detail_page(self, session, result_url, page_url,
                        single_refence_list, download_url,docid,gettype):
        '''
        发送三次请求
        前两次服务器注册 最后一次正式跳转
        '''
        # 这个header必须设置
        HEADER['Referer'] = result_url
        self.single_refence_list=single_refence_list
        self.session = session
        self.session.cookies.set('cnkiUserKey', self.cnkiUserKey)
        self.download_url=download_url
        self.docid=docid
        # cur_url_pattern_compile = re.compile(
        #     r'.*?filename=(.*?)&.*?DbCode=(.*?)&')
        cur_url_pattern_compile = re.compile(
            r'.*?DbCode=(.*?)&.*?filename=(.*?)&')
        cur_url_set=re.search(cur_url_pattern_compile,page_url)
        # 前两次请求需要的验证参数
        params = {
            'curUrl':'detail.aspx?dbCode=' + cur_url_set.group(1) + '&fileName='+cur_url_set.group(2),
            'referUrl': result_url+'#J_ORDER&',
            'cnkiUserKey': self.session.cookies['cnkiUserKey'],
            'action': 'file',
            'userName': '',
            'td': '1544605318654'
        }
        # 首先向服务器发送两次预请求
        self.session.get(
            'http://i.shufang.cnki.net/KRS/KRSWriteHandler.ashx',
            headers=HEADER,
            params=params)
        self.session.get(
            'http://kns.cnki.net/KRS/KRSWriteHandler.ashx',
            headers=HEADER,
            params=params)
        page_url = 'http://kns.cnki.net' + page_url
        get_res=self.session.get(page_url,headers=HEADER)
        self.pars_page(get_res.text,gettype)
        self.excel.save('data/CAJs/Craw_cnki文献属性.xls')


    def pars_page(self,detail_page,gettype):
        '''
        解析页面信息
        '''
        soup=BeautifulSoup(detail_page,'lxml')
        # 获取作者单位信息
        # orgn_list=soup.find(name='div', class_='wx-tit').find_all('a')
        orgn_list=soup.find(name='div', class_='wx-tit').find('h3').next_sibling.next_sibling.find_all('a')
        # orgn_list=soup.find(name='div', id='authorpart').strings
        self.orgn=''
        if len(orgn_list)==0:
            self.orgn='无单位来源'
        else:
            for o in orgn_list:
                self.orgn+=o.text
        # 获取摘要
        try:
            abstract_list = soup.find(name='span', id='ChDivSummary').strings
            self.abstract=''
            for a in abstract_list:
                self.abstract+=a
        except Exception:
            self.abstract='无摘要'
        # 获取关键词
        self.keywords=''
        try:
            keywords_list = soup.find(name='p', class_='keywords').find_all('a')
            if len(keywords_list) == 0:
                self.keywords = '无单位来源'
            else:
                for k_l in keywords_list:
                    for k in k_l.stripped_strings:
                        self.keywords += k
            # keywords_list = soup.find(name='label', id='catalog_KEYWORD').next_siblings
            # for k_l in keywords_list:
            #     # 去除关键词中的空格，换行
            #     for k in k_l.stripped_strings:
            #         self.keywords+=k
        except Exception:
            self.keywords='无关键词'
        self.wtire_excel(gettype)

    def create_list(self,gettype):
        '''
        整理excel每一行的数据
        标志 序号 题名 作者 单位 关键字 摘要  来源 发表时间 下载地址  后缀
        '''
        self.index+=1
        self.reference_list = []
        file_pattern_compile = re.compile(r'[\\/:\*\?"<>\|]')
        self.single_refence_list[1]=re.sub(file_pattern_compile, '', self.single_refence_list[1])
        self.reference_list.append(self.sheet_name)
        self.reference_list.append(self.docid)
        self.reference_list.append(self.docid+self.single_refence_list[1])
        self.reference_list.append(self.single_refence_list[2])
        self.reference_list.append(self.orgn)
        self.reference_list.append(self.keywords)
        self.reference_list.append(self.abstract)
        # for i in range(3,5):
        self.reference_list.append(self.single_refence_list[3])
        self.reference_list.append(self.single_refence_list[4])
        # if config.crawl_isDownLoadLink=='1':
        self.reference_list.append(self.download_url)
        self.reference_list.append(gettype)
        # filename=os.getcwd()+'/data/CAJs/%s.caj'%(self.docid+self.single_refence_list[1])
        # self.reference_list.append(filename)
        print(self.reference_list)


    def wtire_excel(self,gettype):
        '''
        将获得的数据写入到excel
        '''
        self.create_list(gettype)
        for i in range(0, 11):
            self.sheet.write(self.index, i, self.reference_list[i], self.basic_style)

    def set_style(self):
        '''
        设置excel样式
        '''
        self.sheet.col(1).width = 256 * 30
        self.sheet.col(2).width = 256 * 15
        self.sheet.col(3).width = 256 * 20
        self.sheet.col(4).width = 256 * 20
        self.sheet.col(5).width = 256 * 60
        self.sheet.col(6).width = 256 * 15
        self.sheet.col(9).width = 256 * 15
        self.sheet.row(0).height_mismatch=True
        self.sheet.row(0).height = 20*20
        self.basic_style=xlwt.XFStyle()
        al=xlwt.Alignment()
        # 垂直对齐
        al.horz = al.HORZ_CENTER
        # 水平对齐
        al.vert =al.VERT_CENTER
        # 换行
        al.wrap = al.WRAP_AT_RIGHT
        # 设置边框
        borders = xlwt.Borders()
        borders.left = 6
        borders.right = 6
        borders.top = 6
        borders.bottom = 6

        self.basic_style.alignment=al
        self.basic_style.borders=borders

    def set_new_guid(self):
        '''
        生成用户秘钥
        '''
        guid=''
        for i in range(1,32):
            n = str(format(math.floor(random.random() * 16.0),'x'))
            guid+=n
            if (i == 8) or (i == 12) or (i == 16) or (i == 20):
                guid += "-"
        return guid
# 实例化
page_detail = PageDetail()