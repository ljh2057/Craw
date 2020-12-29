# -*- coding: UTF-8 -*-
import requests
import base64
from .GetConfig import config

class CrackVerifyByBaiduOcr:
    def __init__(self, code_url, img_path):
        self.AK = config.baidu_AK
        self.SK = config.baidu_SK
        self.code_url = code_url
        self.img_path = img_path
        self.access_token = self.get_access_token()

    def get_access_token(self):
        token_host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}'.format(
            ak=self.AK, sk=self.SK)
        header = {'Content-Type': 'application/json; charset=UTF-8'}
        response = requests.post(url=token_host, headers=header)
        content = response.json()
        access_token = content.get("access_token")
        return access_token

    def getCode(self):
        header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        def read_img():
            with open(self.img_path, "rb")as f:
                return base64.b64encode(f.read()).decode()

        image = read_img()
        response = requests.post(url=self.code_url, data={"image": image, "access_token": self.access_token},
                                 headers=header)
        return response.json()

