from selenium import webdriver
import threading
import requests
import config


driver = webdriver.Chrome("./chromedriver.exe")
driver.set_window_size(800, 500)
driver.implicitly_wait(3)


def _login():
    driver.get(config.router_host+'/login/login.cgi')
    driver.implicitly_wait(2)
    driver.find_element_by_name('username').send_keys(config.router_login_info['username'])
    driver.find_element_by_name('passwd').send_keys(config.router_login_info['password'])
    driver.find_element_by_id("submit_bt").click()
    driver.implicitly_wait(1)
    driver.find_element_by_tag_name('area').click()
    driver.implicitly_wait(2)


def _find_connected_device():
    driver.refresh()
    driver.implicitly_wait(1)
    driver.switch_to.frame('main_body')
    driver.switch_to.frame('navi_menu_advance')
    driver.find_element_by_id('advance_setup_td').click()
    driver.find_element_by_id('netconf_setup_td').click()
    driver.find_element_by_id('netconf_lansetup_3_td').click()
    driver.switch_to.parent_frame()
    driver.switch_to.frame('main')
    driver.switch_to.frame('lan_pcinfo')

    devices_info = driver.find_element_by_name('lan_pcinfo_fm').text
    _target_device = _has_target_device(devices_info)
    if not _target_device:
        try:
            requests.post(url=config.message_server_host, data={'text': '할머니 전화 전원 확인 필요'}, timeout=20,
                          headers={'Content-Type': 'application/x-www-form-urlencoded'})
        except requests.exceptions.Timeout:
            print('메시지 요청 timeout,  할머니 전화 전원 확인 필요')

    threading.Timer(60*5, _find_connected_device).start()


def _has_target_device(devices_info):
    info = devices_info.split('\n')
    for i in info:
        if -1 != i.find('192.168.5.10 ') or -1 != i.find('android-b25ca991bece99f '):
            return True
    return False


def watch_phone():
    _login()
    _find_connected_device()



