# -*- coding:utf-8 -*-
# Author : air-wind
# Data : 2019/11/22 16:08
import datetime
import time
import json
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, \
    TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait

from TieUrlMap import url_map
from setting import reply_msgs, INTERVAL_MAX, INTERVAL_MIN

# 超时等待时间
WAITTIMEOUT = 5
LOOPDINGINTERVAL = 60 * 60


class DingTie(object):
    def __init__(self, mode):
        self.mode = mode
        self.init_flag = False

    def create_driver(self):
        if self.mode == "production":
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = webdriver.Chrome()

    def ready_windows(self):
        # 修改，一次性打开所有窗口，避免每次打开消耗时间
        now_handle = self.driver.current_window_handle
        for url in url_map:
            # 新开一个窗口
            js = f"window.open('{url}');"
            self.driver.execute_script(js)

        # 获取当前窗口句柄集合（列表类型）
        self.driver.switch_to.window(now_handle)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def init_driver(self):
        if not self.init_flag:
            self.create_driver()
            self.ready_windows()
            self.init_flag = True

    def loop_ding(self):
        handles = self.driver.window_handles
        start_time = time.time()
        while (time.time() - start_time) < LOOPDINGINTERVAL:
            for handle in handles:
                self.driver.switch_to.window(handle)
                self._ding(ding_model="delete")
                time.sleep(random.uniform(2, 6))
            time.sleep(random.uniform(INTERVAL_MIN, INTERVAL_MAX))
        else:
            self._log_print("此ck顶贴完毕，等待另一个ck加载")

    # 获取随机回复
    def _get_reply_msg(self):
        reply_msg = random.choice(reply_msgs)
        random_string = "".join(random.sample(string.ascii_letters + '!#$%&()*+,-./:;<=>?@[\\]^_`{|}~', 2))
        return reply_msg + random_string

    # 顶贴
    def _ding(self, ding_model=None):
        # 定位回复框
        WebDriverWait(self.driver, WAITTIMEOUT, ignored_exceptions=(ElementClickInterceptedException,)) \
            .until(lambda x: x.find_elements_by_xpath('//a[text()="回复"]'))[0].click()

        # 模拟send_key()无效，执行js输入顶贴内容
        ding_msg = self._get_reply_msg()
        send_js = f"ueditor_replace = document.getElementById('ueditor_replace'); " \
                  f"ueditor_replace.innerHTML = '<p>{ding_msg}<\p>'"
        self.driver.execute_script(send_js)

        # 点击发送按钮
        time.sleep(1)
        WebDriverWait(self.driver, WAITTIMEOUT) \
            .until(lambda x: x.find_element_by_xpath('//a[contains(string(.), "发 表")]')).click()

        self._log_print("顶贴成功")

        if ding_model == "delete":
            # 获取页码数
            # self.driver.refresh()
            max_index = self.driver.find_element_by_xpath('//li[contains(text(),"回复贴，共")]/span[2]').text
            if max_index != 1:
                try:
                    self.driver.find_elements_by_xpath('//a[text()="尾页"]')[-1].click()
                except Exception:
                    pass

            # 删除
            time.sleep(1)
            timeout_flag = True
            timeout_loop_time = 0
            # 刷新出最新的回复
            self.driver.refresh()
            while timeout_flag and (timeout_loop_time <= 5):
                try:
                    delete_button = WebDriverWait(self.driver, WAITTIMEOUT) \
                        .until(lambda x: x.find_elements_by_xpath('//a[text()="删除"]'))[-1]
                    # delete_button用click()方法点击概率性失效，调用js执行
                    # delete_button.click()
                    self.driver.execute_script("arguments[0].click();", delete_button)
                    self._log_print("找到了删除按钮")
                    timeout_flag = False
                except TimeoutException:
                    self.driver.refresh()
                    self._log_print("未找到删除按钮")
                except ElementClickInterceptedException:
                    self.driver.refresh()
                    self._log_print("点击被打断")
                finally:
                    timeout_loop_time += 1

            time.sleep(1)
            WebDriverWait(self.driver, WAITTIMEOUT) \
                .until(lambda x: x.find_element_by_xpath('//input[@value="确定"]')).click()

        self._log_print("删除成功")

    # 获取ck 浏览器load ck
    def load_ck(self, ck_index=0):
        with open("cookies.json", "r") as f:
            content = f.read()
        cookies = json.loads(content)[ck_index]

        if not self.init_flag:
            self.driver.get("https://tieba.baidu.com/")
        self.driver.delete_all_cookies()
        for ck in cookies:
            if 'sameSite' in ck:
                del ck['sameSite']
            self.driver.add_cookie(ck)

    def run(self):
        # 获取ck 浏览器load ck
        self.load_ck()

        self.loop_ding()

    def change_ck_run(self):
        # 初始化
        self.init_driver()
        # 重载cookies
        change_time = datetime.datetime.now().strftime("%H")
        if (int(change_time) % 2) == 0:
            ck_index = 0
        else:
            ck_index = 1
        self.load_ck(ck_index)
        self._log_print(f"cookies加载完成使用{ck_index}号ck")

        # 刷新所有窗口
        handles = self.driver.window_handles
        for handle in handles:
            self.driver.switch_to.window(handle)
            self.driver.refresh()

        self.loop_ding()

    def _log_print(self, msg):
        i = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}---{msg}")

    def __del__(self):
        self.driver.quit()
        self._log_print("程序结束")


if __name__ == '__main__':
    dt = DingTie("production")
    # dt = DingTie("")

    # 修改如下
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler = BlockingScheduler()
    trigger = IntervalTrigger(seconds=LOOPDINGINTERVAL+30, start_date=(datetime.datetime.now() + datetime.timedelta(seconds=2)))
    scheduler.add_job(dt.change_ck_run, trigger)
    scheduler.start()
    # scheduler.add_job(dt.change_ck_run, 'interval', hours=1, next_run_time=datetime.datetime.now())
    # scheduler.start()
