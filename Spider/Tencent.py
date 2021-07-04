# -*- coding: utf-8 -*-
# @Time     : 2021/7/4 18:43
# @Author   : ruochen
# @Email    : wangrui@ruochen.email
# @File     : Tencent.py
# @Project  : TencentSignIn

import requests
import json
import os
import base64
import hashlib
import hmac
import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chromedriver = "/usr/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromedriver)

# ==============  1.功能开关配置项 ============== #
# 填 on 则开启，开启的同时也需要配置3中的选项，不填或填其他则关闭
IF_SERVER = os.environ['IF_SERVER']  # 选填！是否开启 server 酱通知
IF_WECHAT = os.environ['IF_WECHAT']  # 选填！是否开启企业微信通知
IF_DING = os.environ['IF_DING']  # 选填！是否开启钉钉通知

# ==============  2.消息通知配置项 ============== #
SERVER_SCKEY = os.environ['SERVER_SCKEY']  # 选填！server 酱的 SCKEY
WECHAT_URL = os.environ['WECHAT_URL']  # 选填！企业微信机器人 url
DING_URL = os.environ['DING_URL']  # 选填！钉钉机器人 url
DING_SECRET = os.environ['DING_SECRET']  # 选填！钉钉机器人加签 secret

# ==============  3.准备发送的消息 ============== #
TEXT = ''  # 消息标题
DESP = ''  # 消息内容


def getCookie():
    global driver
    driver.get('https://cloud.tencent.com/login?s_url=https%3A%2F%2Fcloud.tencent.com%2F')
    time.sleep(5)
    cookies = driver.get_cookies()
    with open('cookie.txt', 'w') as f:
        f.write(json.dumps(cookies))
        driver.close()


def SignIn():
    global driver
    global TEXT
    global DESP
    try:
        driver.get('https://cloud.tencent.com/act/integralmall?from=14376')
        with open('cookie.txt', 'r') as f:
            cookie = f.read()
            cookie = json.loads(cookie)
        for c in cookie:
            driver.add_cookie(c)

        time.sleep(1)
        # 刷新页面
        driver.refresh()
        driver.find_element_by_class_name('bmh-oviewcard-cbtns-btn').click()
        driver.find_element(By.XPATH, '//span[text()="立即签到"]').click()

        DESP = driver.find_element_by_class_name('bmh-oviewcard-cbtns-remind').text
        DESP += driver.find_element_by_class_name('bmh-oviewcard-cbtns-bouns').text
        TEXT = '签到成功！'
    except Exception:
        TEXT = '签到失败！'
        DESP = '签到失败'


class Notice:
    @staticmethod
    def server():
        requests.get('https://sc.ftqq.com/{}.send?text={}&desp={}'.format(SERVER_SCKEY, TEXT, DESP))

    @staticmethod
    def wechat():
        data = {
            'msgtype': 'text',
            'text': {
                'content': DESP
            }
        }
        headers = {'content-type': 'application/json'}
        requests.post(url=WECHAT_URL, headers=headers, data=json.dumps(data))

    @staticmethod
    def ding():
        timestamp = str(round(time.time() * 1000))
        secret = DING_SECRET
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        headers = {'Content-Type': 'application/json'}
        complete_url = DING_URL + '&timestamp=' + timestamp + "&sign=" + sign
        data = {
            "text": {
                "content": DESP
            },
            "msgtype": "text"
        }
        requests.post(url=complete_url, data=json.dumps(data), headers=headers)


if __name__ == '__main__':
    SignIn()
