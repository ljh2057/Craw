import requests
from bs4 import BeautifulSoup
from plugins.Craw_baidu import getxml
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import xlwt, xlrd
from xlutils.copy import copy
import os


class Baidu(object):
	# 参考：https://www.jianshu.com/p/b9068070785a
	# 当前时间
	t = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
	# 构建CRID
	CRID = 'CRA' + t
	# path = getxml.rxi.getpropertypath()
	# propertypath = path + '/baidujs.xls'



	def __init__(self, filepath = None):
		# 初始网页
		self.start_url = 'https://news.baidu.com/mil'
		self.t = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
		# 构建CRID
		self.CRID = 'CRA' + self.t
		self.num = 0
		self.filepath = filepath
		if self.filepath is None:
			self.filepath = getxml.rxi.getfilepath()
		# 定义保存Excel的位置
		self.workbook = xlwt.Workbook()
		self.sheet = self.workbook.add_sheet('百度军事')
		# 设置Excel表头
		# head = ['标题', '发布者', 'CRID', 'DOCID', '内容', 'url']
		head = ['标志', '序号', '题名', '作者', '单位', '关键字', '摘要', '来源', '发表时间', '下载地址', '后缀']
		for h in range(len(head)):
			self.sheet.write(0, h, head[h])  # 把表头写到Excel里面去

	# 获取每条新闻的url
	def geturls(self):
		chrome_options = Options()
		chrome_options.add_argument('--headless')  # 使用无头谷歌浏览器模式
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		browser = webdriver.Chrome(chrome_options=chrome_options)
		browser.get(self.start_url)
		# 设置滚动条距离顶部的位置，设置为 10000， 超过10000就是最底部
		js = 'var action=document.documentElement.scrollTop=10000'
		# 回到顶部
		js1 = 'var action=document.documentElement.scrollTop=0'
		# 滚起来！
		browser.execute_script(js)  # 执行脚本
		time.sleep(1)
		browser.execute_script(js)
		time.sleep(1)
		browser.execute_script(js1)
		time.sleep(1)
		browser.execute_script(js)
		time.sleep(1)
		html = browser.page_source
		browser.quit()
		# 使用BeautifulSoup模块对页面文件进行解析
		soup = BeautifulSoup(html, 'html.parser')
		url_list = []
		for item in soup.select('#col_guojijq > div > div > ul > li > a'):
			url = item.get('href')
			url_list.append(url)
			# print(url)
		return url_list

	# 获取页面具体信息
	def getdetail(self, news_url):
		response = requests.get(news_url)
		html = response.text
		bf = BeautifulSoup(html, 'html.parser')
		# print("开始爬取。。。。。。。。。。。。")
		# url
		self.newsurl = news_url
		# print("url:"+self.newsurl)

		# 标题
		# self.title = bf.select("#detail-page > div.title_border > div > div.article-title > h2")[0].get_text()
		try:
			self.title = bf.select("#detail-page > div.title_border > div > div.article-title > h2")[0].get_text()
		except:
			pass
		# print("title:"+self.title)

		# 发布者
		self.poster = bf.select(
			"#detail-page > div.title_border > div > div.article-desc.clearfix > div.author-txt > p")[0].get_text()
		# print("poster:"+self.poster)

		# 时间
		self.time1 = bf.select(
			"#detail-page > div.title_border > div > div.article-desc.clearfix > div.author-txt > div > span.date")[0].\
			get_text()
		self.time = str(time.localtime().tm_year)+'-'+self.time1.strip("发布时间：")


		# 内容
		self.content_list = []
		content = bf.select("#article > div > p > span")
		# print("content:")
		for c in content:
			# print(c.get_text())
			self.content_list.append(c.get_text())
		# print(self.content_list)

		# DOCID
		self.num += 1
		self.DOCID = self.CRID + "%04d" % self.num
		# print("DOCID:"+self.DOCID)
		# print("CRID:"+self.CRID)

		self.write_excel()
		self.write_txt()

	def write_txt(self):
		txtname = self.DOCID + self.title
		txtpath = self.filepath.replace('\\', '/') + "/" + txtname + ".txt"
		# print("写入txt：" + txtpath)
		writetxt = open(txtpath, "w")
		for i in range(len(self.content_list)):
			writetxt.write(self.content_list[i])
		writetxt.close()

		# head = ['标志', '序号', '题名', '作者', '单位', '关键字', '摘要', '来源', '发表时间', '下载地址', '后缀']
	def write_excel(self):
		self.sheet.write(self.num, 0, self.CRID)
		self.sheet.write(self.num, 1, self.DOCID)
		self.sheet.write(self.num, 2, self.DOCID+self.title)
		self.sheet.write(self.num, 3, self.poster)
		self.sheet.write(self.num, 8, self.time)
		self.sheet.write(self.num, 9, self.newsurl)
		self.sheet.write(self.num, 10, 'txt')
	# 	# 追加写入 参考：https://blog.csdn.net/lA6Nf/article/details/79352112?utm_source=blogxgwz6
	# 	rb = xlrd.open_workbook(self.propertypath, formatting_info=True)
	# 	rn = rb.sheets()[0].nrows
	# 	# r = rn
	# 	# print(rn)
	# 	wb = copy(rb)
	# 	st = wb.get_sheet(0)
	# 	self.write_excel(st, rn)
	# 	os.remove(self.propertypath)
	# 	wb.save(self.propertypath)

		# return self.num, self.title

	# 写入excel
	# def write_excel(self, sheet, n):
	# 	sheet.write(n, 0, self.title)
	# 	sheet.write(n, 1, self.poster)
	# 	sheet.write(n, 2, self.CRID)
	# 	sheet.write(n, 3, self.DOCID)
	# 	sheet.write(n, 4, self.content_list)
	# 	sheet.write(n, 5, self.newsurl)



# if __name__ == "__main__":
	# bd = Baidu()
	# urls = []
	# urls = bd.geturls()
	# # c = []
	# for url in urls:
	# 	if int(bd.num) < 10:
	# 		bd.getdetail(url)
	# 	else:
	# 		break
	# 	# print(int(bd.num)+1)
	# 	# bd.getdetail(url)
	# 	# c.append(bd.getdetail(url))
	# # bd.workbook.save('E:/Pythonworkspace/bdjs_crawl/baidujs.xls')
	# # print(c)
	# t = time.strftime('%Y', time.localtime(time.time()))
	# print(time.localtime().tm_year)
	# print()



