from selenium import webdriver
import threading
import requests
import config


class PhoneWatcher:
    def __init__(self):
        self._init_driver()
        self._login()
        self._find_connected_device()

    def _init_driver(self):
        self.driver = webdriver.Chrome("./chromedriver.exe")
        self.driver.set_window_size(800, 500)
        self.driver.implicitly_wait(10)

    def _login(self):
        self.driver.get(config.router_host+'/login/login.cgi')
        self.driver.find_element_by_name('username').send_keys(config.router_login_info['username'])
        self.driver.find_element_by_name('passwd').send_keys(config.router_login_info['password'])
        self.driver.find_element_by_id("submit_bt").click()
        self.driver.find_element_by_tag_name('area').click()

    def _find_connected_device(self):
        self.driver.refresh()
        self.driver.switch_to.frame('main_body')
        self.driver.switch_to.frame('navi_menu_advance')
        self.driver.find_element_by_id('advance_setup_td').click()
        self.driver.find_element_by_id('netconf_setup_td').click()
        self.driver.find_element_by_id('netconf_lansetup_3_td').click()
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('main')
        self.driver.switch_to.frame('lan_pcinfo')

        devices_info = self.driver.find_element_by_name('lan_pcinfo_fm').text
        target_device = self._has_target_device(devices_info)
        if not target_device:
            try:
                requests.post(url=config.message_server_host, data={'text': '할머니 전화 전원 확인 필요'}, timeout=20,
                              headers={'Content-Type': 'application/x-www-form-urlencoded'})
            except requests.exceptions.Timeout:
                print('메시지 요청 timeout,  할머니 전화 전원 확인 필요')

        threading.Timer(60*5, self._find_connected_device).start()

    @staticmethod
    def _has_target_device(devices_info):
        info = devices_info.split('\n')
        for i in info:
            if -1 != i.find('192.168.5.10 ') or -1 != i.find('android-b25ca991bece99f '):
                return True
        return False


def watch_phone():
    PhoneWatcher()
