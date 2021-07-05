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

# ==============  1.登录信息 ============== #
EMAIL = os.environ['EMAIL']  # 邮箱地址
PWD = os.environ['PWD']      # 登录密码
print(EMAIL, PWD)

# ==============  2.功能开关配置项 ============== #
# 填 on 则开启，开启的同时也需要配置3中的选项，不填或填其他则关闭
IF_SERVER = os.environ['IF_SERVER']  # 选填！是否开启 server 酱通知
IF_PUSHPLUS = os.environ['IF_PUSHPLUS']  # 选填！是否开始 pushplus 通知
# IF_WECHAT = os.environ['IF_WECHAT']  # 选填！是否开启企业微信通知
IF_DING = os.environ['IF_DING']  # 选填！是否开启钉钉通知

# ==============  3.消息通知配置项 ============== #
SERVER_SCKEY = os.environ['SERVER_SCKEY']  # 选填！server 酱的 SCKEY
TOKEN = os.environ['TOKEN']
# WECHAT_URL = os.environ['WECHAT_URL']  # 选填！企业微信机器人 url
DING_URL = os.environ['DING_URL']  # 选填！钉钉机器人 url
DING_SECRET = os.environ['DING_SECRET']  # 选填！钉钉机器人加签 secret

# ==============  4.准备发送的消息 ============== #
TEXT = ''  # 消息标题
DESP = ''  # 消息内容

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chromedriver = "/usr/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver)
# driver = webdriver.Chrome(chrome_options=chrome_options)

def getCookie():
    global driver
    driver.get('https://cloud.tencent.com/login?s_url=https%3A%2F%2Fcloud.tencent.com%2F')
    time.sleep(5)
    cookies = driver.get_cookies()
    with open('cookie.txt', 'w') as f:
        f.write(json.dumps(cookies))
        driver.close()

def login():
    global driver
    driver.get('https://cloud.tencent.com/login?s_url=https%3A%2F%2Fcloud.tencent.com%2F')
    # clg = driver.find_element_by_class_name('clg-other-con')
    # print(clg)
    driver.find_element(By.XPATH, '//div[@class="clg-other-con J-switchLoginTypeArea"]/div[1]').click()
    driver.find_element_by_class_name('J-username').send_keys(EMAIL)
    driver.find_element_by_class_name('J-password').send_keys(PWD)
    driver.find_element_by_class_name('J-loginBtn').click()
    try:
        tip = driver.find_element_by_class_name('J-loginTip').text
        return None
    except Exception:
        pass
    return driver
        
def SignIn():
    global TEXT
    global DESP
#     if driver is None:
#         TEXT = '签到失败'
#         DESP = '登录失败，账号或密码错误！'
#         return
    try:
        driver.get('https://cloud.tencent.com/act/integralmall?from=14376')
        with open('cookie.txt', 'r') as f:
            cookie = json.load(f)
        for c in cookie:
            driver.add_cookie(c)

        time.sleep(2)
        刷新页面
        driver.refresh()
        html = driver.execute_script("return document.documentElement.outerHTML")
        print(html)
        time.sleep(0.5)
        driver.find_element_by_class_name('bmh-oviewcard-cbtns-btn').click()
        driver.find_element(By.XPATH, '//span[text()="立即签到"]').click()
        driver.refresh()

        DESP = driver.find_element_by_class_name('bmh-oviewcard-cbtns-remind').text
        DESP += driver.find_element_by_class_name('bmh-oviewcard-cbtns-bouns').text
        TEXT = '签到成功！'
    except Exception as e:
        TEXT = '签到失败！'
        DESP = '签到失败'
        print(e)


class Notice:
    
    @staticmethod
    def pushplus():
        requests.get(
            'http://www.pushplus.plus/send?token={}&title={}&content={}&ttemplate=html'.format(TOKEN, TEXT, DESP))
        
    @staticmethod
    def server():
        requests.get('https://sctapi.ftqq.com/{}.send?text={}&desp={}'.format(SERVER_SCKEY, TEXT, DESP))

    '''
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
    '''

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


def run():
    n = Notice()
#     driver = login()
#     SignIn(driver)
    SignIn()
    print(TEXT, DESP)

    if IF_SERVER == 'on':
        n.server()
    # if IF_WECHAT == 'on':
    #     n.wechat()
    if IF_PUSHPLUS == 'on':
        n.pushplus()
    if IF_DING == 'on':
        n.ding()


if __name__ == '__main__':
    run()
