# -*- coding:utf-8 -*-
# Author : air-wind
# Data : 2019/11/22 16:08

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import json
import random

from TieUrlMap import url_map
from setting import reply_msgs, INTERVAL_MAX, INTERVAL_MIN

class DingTie(object):
    def __init__(self):
        pass

    def create_driver(self, mode="production"):
        if mode == "production":
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = webdriver.Chrome()

    def loop_ding(self):
        while True:
            for url in url_map:
                self.driver.get(url)
                self._ding()
                time.sleep(random.uniform(INTERVAL_MIN, INTERVAL_MAX))

    # 获取随机回复
    def _get_reply_msg(self):
        reply_msg = random.sample(reply_msgs,1)[0]
        return reply_msg

    # 顶贴
    def _ding(self):
        # 定位回复框
        time.sleep(1)
        reply_href = self.driver.find_element_by_xpath('/html/body/ul/li[2]/a')
        reply_href.click()

        # 模拟send_key()无效，执行js输入顶贴内容
        ding_msg = self._get_reply_msg()
        send_js = f"ueditor_replace = document.getElementById('ueditor_replace'); " \
            f"ueditor_replace.innerHTML = '<p>{ding_msg}<\p>'"
        self.driver.execute_script(send_js)

        # 点击发送按钮
        time.sleep(1)
        send_button = self.driver.find_element_by_xpath('//*[@id="tb_rich_poster"]/div[3]/div[3]/div/a/span/em')
        send_button.click()

    # 获取ck 浏览器load ck
    def load_ck(self):
        with open("cookies.json", "r") as f:
            content = f.read()
        cookies = json.loads(content)

        self.driver.get("https://tieba.baidu.com/")
        self.driver.delete_all_cookies()
        for ck in cookies:
            if 'sameSite' in ck:
                del ck['sameSite']
            self.driver.add_cookie(ck)

    def run(self):
        # 配置driver
        self.create_driver(mode="dev")

        # 获取ck 浏览器load ck
        self.load_ck()

        self.loop_ding()


if __name__ == '__main__':
    dt = DingTie()
    dt.run()
