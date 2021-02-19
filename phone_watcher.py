from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import requests
import config
import time


class PhoneWatcher:
    def __init__(self):
        self._init_driver()
        self._first_check_time = None
        self._last_post_time = None
        self._request_cnt = 0
        self.request_term = 60*3-20

    def _init_driver(self):
        self.driver = webdriver.Chrome("./chromedriver.exe")
        self.driver.set_window_size(800, 500)

    def _login(self):
        self.driver.get(config.router_host+'/login/login.cgi')
        try:
            self.driver.find_element(By.NAME, 'username').send_keys(config.router_login_info['username'])
            self.driver.find_element(By.NAME, 'passwd').send_keys(config.router_login_info['password'])
            self.driver.find_element(By.ID, "submit_bt").click()
        finally:
            self.driver.find_element(By.TAG_NAME, 'area').click()

    def switch_to_lan_pcinfo(self):
        self.driver.switch_to.frame('main_body')
        self.driver.switch_to.frame('navi_menu_advance')
        self.driver.find_element(By.ID, 'advance_setup_td').click()
        self.driver.find_element(By.ID, 'netconf_setup_td').click()
        self.driver.find_element(By.ID, 'netconf_lansetup_3_td').click()
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('main')
        self.driver.switch_to.frame('lan_pcinfo')

    def _find_connected_device(self):
        if len(self.driver.find_elements(By.NAME, 'lan_pcinfo_fm')) == 0:
            self.switch_to_lan_pcinfo()
        devices_info = self.driver.find_element(By.NAME, 'lan_pcinfo_fm').text
        return self._has_target_device(devices_info)

    @staticmethod
    def _has_target_device(devices_info):
        info = devices_info.split('\n')
        for i in info:
            if -1 != i.find('192.168.5.10') or -1 != i.find('android-b25ca991bece99f'):
                return True
        return False

    def _check_device(self):
        target_device = self._find_connected_device()
        self._request_cnt += 1
        if target_device:
            self._request_cnt = 0
            self._last_post_time = None
        elif self._request_cnt == 2 or (self._last_post_time is not None and time.time() - self._last_post_time > 3600):
            self._last_post_time = time.time()
            try:
                requests.post(url=config.message_server_host, data={'text': '할머니 전화 전원 확인 필요'}, timeout=20,
                              headers={'Content-Type': 'application/x-www-form-urlencoded'})
            except requests.exceptions.Timeout:
                print('메시지 요청 timeout,  할머니 전화 전원 확인 필요')

    def start(self):
        try:
            if -1 == self.driver.current_url.find("/sess-bin/timepro.cgi"):
                self._login()

            if self._first_check_time is None:
                self._first_check_time = time.time()

            self._check_device()

            # 로그인 세션(60분) 만료 방지 새로고침
            if time.time() - self._first_check_time > 3300:
                self._first_check_time = None
                self.driver.refresh()

        finally:
            threading.Timer(self.request_term, self.start).start()


def watch_phone():
    watcher = PhoneWatcher()
    watcher.start()
