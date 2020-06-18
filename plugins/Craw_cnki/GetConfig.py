# import os
# import configparser
#
class LazyProperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class GetConfig(object):
    """
    to get config from config.ini
    """
    # def __init__(self):
        # self.conf=configparser.ConfigParser()
        # self.conf.read('./Config.ini', encoding='UTF-8')


    @LazyProperty
    def crawl_isdownload(self):
        return '1'
        # print(self.conf.get('crawl','isDownloadFile'))
        # return self.conf.get('crawl','isDownloadFile')

    @LazyProperty
    def crawl_iscrackcode(self):
        return 0

        # return self.conf.get('crawl', 'isCrackCode')


    @LazyProperty
    def crawl_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.3',
            'Host': 'kdoc.cnki.net',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }
        return headers

    @LazyProperty
    def crawl_isdetail(self):
        return 1

        # return self.conf.get('crawl', 'isDetailPage')

    @LazyProperty
    def crawl_stepWaitTime(self):
        return 2
        # return int(self.conf.get('crawl', 'stepWaitTime'))

    @LazyProperty
    def crawl_isDownLoadLink(self):
        return 1

        # return int(self.conf.get('crawl', 'isDownLoadLink'))

config=GetConfig()

