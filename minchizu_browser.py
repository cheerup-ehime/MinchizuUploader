# coding:utf-8
import os
import pandas as pd
from datetime import datetime

from selenium import webdriver
import numpy as np
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
import location_importer as lim

url_minchizu = 'https://minchizu-dev.firebaseapp.com/'

def get_now_string():
    return datetime.now().strftime('%Y/%m/%d %H:%M:%S')


class MinchizuBrowser:
    info_types = {
        '給水所': 'rb-16-0',
        '入浴施設': 'rb-17-0',
        '洗濯': 'rb-18-0',
        '入浴施設': 'rb-19-0',
        '通行止め': 'rb-20-0',
        '公共交通機関情報': 'rb-21-0',
        'ボランティア募集／センター': 'rb-22-0',
        '物資拠点': 'rb-23-0',
        '被害報告': 'rb-24-0',
    }

    @staticmethod
    def build_driver():
        options = Options()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url_minchizu)
        return driver

    def __init__(self, url='https://minchizu-e6818.firebaseapp.com/'):
        self.driver = MinchizuBrowser.build_driver()

    def scroolByElementAndOffset(self, element, offset = 0):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

        if offset != 0:
            script = "window.scrollTo(0, window.pageYOffset + " + str(offset) + ");"
            self.driver.execute_script(script)

    def show_minchizu(self):
        self.driver.get(url_minchizu)

    def show_register_info(self):
        #情報を登録を押す
        register_button = self.driver.find_element_by_xpath("//a[@id='tab-t0-2']")
        assert register_button is not None
        print(register_button.get_attribute('aria-selected'))
        register_button.click()

    def to_ymd_for_input_date(self, ymd):
        year, month, day = ymd.split('/')
        year = "{:06d}".format(int(year))
        month = "{:02d}".format(int(month))
        day = "{:02d}".format(int(day))
        return "{}{}{}".format(year, month, day)

    def fill_location(self, row):
        # 緯度経度を取得
        lat = self.driver.find_element_by_xpath("//input[@name='latitude']")
        assert lat is not None
        lat.send_keys(str(row.lat))

        lng = self.driver.find_element_by_xpath("//input[@name='longitude']")
        assert lng is not None
        lng.send_keys(str(row.lng))

        title = self.driver.find_element_by_xpath("//input[@name='title']")
        assert title is not None
        title.send_keys(row.location)

        contributor = self.driver.find_element_by_xpath("//input[@name='contributor']")
        assert contributor is not None
        contributor.send_keys(row.contributor)

        desc = self.driver.find_element_by_xpath("//textarea[@name='description']")
        assert desc is not None
        description = "【時間帯】：{}\n\n【情報元】：{}\n\n【説明】：\n\n{}".format(
            row.time_slot, row.original_info, row.description)
        desc.send_keys(description)

        period_from = self.driver.find_element_by_xpath("//input[@ng-reflect-name='viewPeriodFrom']")
        assert period_from is not None
        if row.period_from != '' or pd.notnull(row.period_from):
            period_from.click()
            period_from.send_keys(self.to_ymd_for_input_date(row.period_from))

        period_to = self.driver.find_element_by_xpath("//input[@ng-reflect-name='viewPeriodTo']")
        assert period_to is not None
        if row.period_to != '' or pd.notnull(row.period_to):
            period_to.click()
            period_to.send_keys(self.to_ymd_for_input_date(row.period_to))

        info_type = MinchizuBrowser.info_types[row.type]
        assert info_type is not None

        option_button = self.driver.find_element_by_xpath("//button[@id='{}']".format(info_type))
        assert option_button is not None
        option_button.click() #toggle true/false

        assert option_button.get_attribute('aria-checked') == "true"

    def submit(self):
        submit_button = \
            self.driver.find_element_by_xpath(
                "//span[contains(text(), '投稿') and @class='button-inner']/..")
        assert submit_button is not None

        self.scroolByElementAndOffset(submit_button, 5)
        submit_button.click()

    def close_alert(self):
        close_button = \
            self.driver.find_element_by_xpath(
                "//span[contains(text(), '閉じる') and @class='button-inner']/..")
        assert close_button is not None
        close_button.click()



def register_locations(df, url=None):
    browser = MinchizuBrowser(url)
    browser.show_minchizu()

    status_list = []
    updates_list = []

    browser.show_register_info()
    sleep(2)

    for index, row in df.iterrows():
        print('{}: {}.{}'.format(row.location, row.lat, row.lng))

        if pd.isnull(row.lat):
            status_list.append('FAIL')
            updates_list.append('')
            print('skipping : {}'.format(row.location))
            continue

        browser.fill_location(row)
        browser.submit()
        sleep(2)
        browser.close_alert()

        browser.driver.save_screenshot('search_results.png')

        status_list.append('DONE')
        updates_list.append(get_now_string())

    df.status = status_list
    df.updated = updates_list

    browser.driver.close()
    browser.driver.quit()

    return df




