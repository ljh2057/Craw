# -*- coding:utf-8 -*-

import urllib.request
import json
import re
import lxml.html
import os
from lxml import etree
from random import randint
from datetime import datetime
from plugins.Craw_souhu import getxml
import time
import pandas as pd
import openpyxl

class Souhu(object):
    # 当前时间
    t = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    # 构建CRID
    CRID = 'CRA' + t
    sohu_template_url = 'http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=10&page=1&size={}'
    # sohu_template_url = 'http://www.sohu.com/tag/69932/'
    nets = ['sohu']

    template_urls = {
        'sohu': sohu_template_url,
    }
    most_top = {
        'sohu': 1000,
    }
    latest_news_functions = {
        'sohu': 'self.get_sohu_latest_news',
    }
    xpaths = {
        'sohu': '//*[@id="mp-editor"]/p',
    }
    def __init__(self, filepath=None, args={}):
        self.LATEST_COLS = ['title', 'time', 'url']
        self.LATEST_COLS_C = ['CRID', 'DOCID', 'title', 'time', 'url', 'content']
        self.flag = True
        self.args = args
        self.filepath = filepath
        if self.filepath is None:
            self.filepath = getxml.rxi.getfilepath()
        # self.sohu_template_url = 'http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=10&page=1&size={}'
        # self.nets = ['sohu']
        # self.template_urls = {
        #     'sohu': self.sohu_template_url,
        # }
        # self.most_top = {
        #     'sohu': 1000,
        # }
        # self.latest_news_functions = {
        #     'sohu': 'get_sohu_latest_news',
        # }
        # self.xpaths = {
        #     'sohu': '//*[@id="mp-editor"]/p',
        # }


    # def get_latest_news(self, net, args, path, top=80, show_content=False):
    def get_latest_news(self, net, path, top=80, show_content=False):
        # flag = args['flag']
        # process = args['CrawProcess']  # <class 'PyQt5.QtCore.pyqtBoundSignal'>
        path = path.replace('\\', '/')
        path = path.replace('//', '\\')
        # print(path)
        assert net in self.nets, '参数1(net)错误！应为' + '、'.join(self.nets) + '中的一个！'
        most_top_num = self.most_top[net]
        if top > most_top_num:
            print('top>{}，将获取{}条即时军事新闻'.format(most_top_num, most_top_num))
            top = most_top_num
        latest_news_function = self.latest_news_functions[net]
        template_url = self.template_urls[net]
        df = eval('{}(\'{}\',\'{}\',{},{})'.format(latest_news_function, template_url, path, top, show_content))
        # print(df)
        return df

    def latest_content(self, net, url):
        """获取content"""
        content = ''
        try:
            html = lxml.html.parse(url, parser=etree.HTMLParser(encoding='utf-8'))
            res = html.xpath(self.xpaths[net])
            p_str_list = [etree.tostring(node).strip().decode('utf-8') for node in res]
            content = '\n'.join(p_str_list)
            html_content = lxml.html.fromstring(content)
            content = html_content.text_content()
            content = re.sub(r'(\r*\n)+', '\n', content)
        except Exception as e:
            print(e)
        return content

    def get_sohu_latest_news(self, template_url, path=None, top=80, show_content=True):
    # def get_sohu_latest_news(self, template_url, top=80, show_content=True):
        try:
            path = path.replace('/', '\\')
            # print("path..." + path)
            url = template_url.format(top)
            # url = template_url
            request = urllib.request.Request(url)
            data_str = urllib.request.urlopen(request, timeout=10).read()
            data_str = data_str.decode('utf-8')
            data_str = data_str[1:-1]
            data_str = eval(data_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
            data_str = json.dumps(data_str)
            data_str = json.loads(data_str)
            # print(data_str)
            data = []
            # for r in data_str:
            '''
            for i, r in enumerate(data_str):
                rt = datetime.fromtimestamp(r['publicTime'] // 1000)
                # time
                rt_str = datetime.strftime(rt, '%Y-%m-%d %H:%M')
                # url
                r_url = 'http://www.sohu.com/a/' + str(r['id']) + '_' + str(r['authorId'])
                # DOCID
                DOCID = self.CRID + "%04d" % (i + 1)
                # print(DOCID)
                # print(r_url)
                row = [self.CRID, DOCID, r['title'], rt_str, r_url]
                if show_content:
                    print('downloading %s' % r['title'])
                    row.append(self.latest_content('sohu', r_url))
                data.append(row)
            '''
            for i, r in enumerate(data_str):
                if i < top:
                    rt = datetime.fromtimestamp(r['publicTime'] // 1000)
                    # time
                    rt_str = datetime.strftime(rt, '%Y-%m-%d %H:%M')
                    # url
                    r_url = 'http://www.sohu.com/a/' + str(r['id']) + '_' + str(r['authorId'])
                    # DOCID
                    DOCID = self.CRID + "%04d" % (i + 1)
                    row = [self.CRID, DOCID, r['title'], rt_str, r_url]
                    # if show_content and self.flag:
                    # print(self.flag)
                    if self.flag==True:
                        if show_content:
                            # print(flag)
                            print('downloading %s' % r['title'])
                            self.pg="正在下载第%d篇新闻:%s"%(i+1, r['title'])
                            # print(type(self.args["CrawProcess"]))
                            self.args["CrawProcess"].emit(str(self.pg))
                            row.append(self.latest_content('sohu', r_url))
                            # 写入TXT
                            txtname = row[1] + row[2]
                            tn = re.sub(r'[\/:*?"<>|]', '-', txtname)
                            # tn = txtname.replace('"', '')
                            # tn = tn.replace(':', '')
                            # tn = tn.replace('?', '')
                            txtpath = str(path).replace('\\', '/') + "/" + tn + ".txt"
                            writetxt = open(txtpath, "w")
                            writetxt.write(row[5].encode("gbk", 'ignore').decode("gbk", "ignore"))
                            writetxt.close()
                        data.append(row)

            df = pd.DataFrame(data, columns=self.LATEST_COLS_C if show_content else self.LATEST_COLS)
            # print(df)
            return df
        except Exception as e:
            print(e)

    # def save_to_txt(self, news_df, path, top=80):
    #     "保存到TXT"
    #     for i in range(top):
    #         txtname = news_df['DOCID'][i] + news_df['title'][i]
    #         tn = txtname.replace('"', '')
    #         txtpath = str(path).replace('\\', '/') + "/" + tn + ".txt"
    #         # txtpath = str(path)+ "\\" + txtname + ".txt"
    #         # print("写入txt：" + txtpath)
    #         writetxt = open(txtpath, "w")
    #         writetxt.write(news_df['content'][i].encode("gbk", 'ignore').decode("gbk", "ignore"))
    #         writetxt.close()

    def save_news(self, news_df, path):
        """保存新闻"""
        # print(type(news_df))
        # print(news_df)
        # news_df.to_csv(path, index=False, encoding='gb18030')
        # #to_excel
        news_df.to_excel(path, index=False, na_rep=None)
        wb = openpyxl.load_workbook(path)
        ws = wb.worksheets[0]
        ws.insert_cols(4, 5)
        for index, row in enumerate(ws.rows):
            if index == 0:
                row[0].value = '标志'
                row[1].value = '序号'
                row[2].value = '题名'
                row[3].value = '作者'
                row[4].value = '单位'
                row[5].value = '关键字'
                row[6].value = '摘要'
                row[7].value = '来源'
                row[8].value = '发表时间'
                row[9].value = '下载地址'
                row[10].value = '后缀'
            else:
                row[3].value = None
                row[4].value = None
                row[5].value = None
                row[6].value = None
                row[7].value = None
                row[10].value = None
        wb.save(path)
        # # print("filepath......" + os.path.join(path, 'sohu_latest_news.csv'))
        # path = path.replace('\\', '/')
        # print(path)
        # df = pd.read_csv(path, encoding='gb18030')
        # df = df.astype(str)
        # df.insert(2, 'hhhhhhh', '')
        # # news_df.to_csv(path, index=False)

    def replace_line_terminator(self, x):
        """替换行终止符"""
        try:
            x = re.sub(r'\r\n', '\n', x)
        except TypeError:
            pass
        return x

    def load_news(self, path):
        """加载新闻"""
        news_df = pd.read_csv(path, encoding='gb18030')
        news_df = news_df.applymap(self.replace_line_terminator)
        return news_df


'''
LATEST_COLS = ['title', 'time', 'url']
# LATEST_COLS_C = ['title', 'time', 'url', 'content']
LATEST_COLS_C = ['CRID', 'DOCID', 'title', 'time', 'url', 'content']
# LATEST_COLS_C = ['CRID', 'title', 'time', 'url', 'content']
# LATEST_COLS_C = ['标志', '序号', 'title', '作者', '单位', '关键字', '摘要', '来源', 'time', 'url', '后缀', 'content']


sohu_template_url = 'http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=10&page=1&size={}'
# sohu_template_url = 'http://www.sohu.com/tag/69932/'
nets = ['sohu']

template_urls = {
    'sohu': sohu_template_url,
}
most_top = {
    'sohu': 1000,
}
latest_news_functions = {
    'sohu': 'get_sohu_latest_news',
}
xpaths = {
    'sohu': '//*[@id="mp-editor"]/p',
}

# 当前时间
t = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
# 构建CRID
CRID = 'CRA' + t
# num = 0


def get_latest_news(net, top=80, show_content=False):

    assert net in nets, '参数1(net)错误！应为' + '、'.join(nets) + '中的一个！'
    most_top_num = most_top[net]
    if top > most_top_num:
        print('top>{}，将获取{}条即时军事新闻'.format(most_top_num, most_top_num))
        top = most_top_num
    latest_news_function = latest_news_functions[net]
    template_url = template_urls[net]
    df = eval('{}(\'{}\',{},{})'.format(latest_news_function, template_url, top, show_content))
    # print(df)
    return df

def latest_content(net, url):
    """获取content"""
    content = ''
    try:
        html = lxml.html.parse(url, parser=etree.HTMLParser(encoding='utf-8'))
        res = html.xpath(xpaths[net])
        p_str_list = [etree.tostring(node).strip().decode('utf-8') for node in res]
        content = '\n'.join(p_str_list)
        html_content = lxml.html.fromstring(content)
        content = html_content.text_content()
        content = re.sub(r'(\r*\n)+', '\n', content)
    except Exception as e:
        print(e)
    return content



def get_sohu_latest_news(template_url, top=80, show_content=False):
    try:
        url = template_url.format(top)
        # url = template_url
        request = urllib.request.Request(url)
        data_str = urllib.request.urlopen(request, timeout=10).read()
        data_str = data_str.decode('utf-8')
        data_str = data_str[1:-1]
        data_str = eval(data_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        data_str = json.dumps(data_str)
        data_str = json.loads(data_str)
        # print(data_str)
        data = []
        # for r in data_str:
        for i, r in enumerate(data_str):
            rt = datetime.fromtimestamp(r['publicTime'] // 1000)
            # time
            rt_str = datetime.strftime(rt, '%Y-%m-%d %H:%M')
            # url
            r_url = 'http://www.sohu.com/a/' + str(r['id']) + '_' + str(r['authorId'])
            # DOCID
            DOCID = CRID + "%04d" % (i+1)
            row = [CRID, DOCID, r['title'], rt_str, r_url]
            if show_content:
                print('downloading %s' % r['title'])
                row.append(latest_content('sohu', r_url))
            data.append(row)
        df = pd.DataFrame(data, columns=LATEST_COLS_C if show_content else LATEST_COLS)
        # print(df)
        return df
    except Exception as e:
        print(e)

def save_to_txt(news_df, path, top=80):
    "保存到TXT"
    for i in range(top):
        txtname = news_df['DOCID'][i] + news_df['title'][i]
        txtpath = str(path).replace('\\', '/') + "/" + txtname + ".txt"
        # print("写入txt：" + txtpath)
        writetxt = open(txtpath, "w")
        writetxt.write(news_df['content'][i])
        writetxt.close()


def save_news(news_df, path):
    """保存新闻"""
    # print(news_df['title'][0])
    news_df.to_csv(path, index=False, encoding='gb18030')
    # news_df.to_csv(path, index=False)


def replace_line_terminator(x):
    """替换行终止符"""
    try:
        x = re.sub(r'\r\n', '\n', x)
    except TypeError:
        pass
    return x


def load_news(path):
    """加载新闻"""
    news_df = pd.read_csv(path, encoding='gb18030')
    news_df = news_df.applymap(replace_line_terminator)
    return news_df
'''