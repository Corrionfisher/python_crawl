#!/usr/bin/env python
# coding: utf-8
# 一共5個自定義參數要依照不同資料做設置
# 本篇為: 華藝線上圖書館


# 導入所需的package
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from glob import glob
import numpy as np


# 設定參數1: 設定查詢名稱與條件

search_name = str('\"台灣社會變遷基本調查\" OR [ALL]:\"Taiwan Social Change Survey\" OR [ALL]:\"TSCS\"') #本篇為: 台灣社會變遷基本調查(TSCS)

# 設定參數2,3: 設定叢集名稱、搜尋來源

pName = str('TSCS') # 叢集名稱(會變成csv檔的名字，盡量用英文簡稱)
datasource = str("華藝線上") # 來源(會出現在csv檔內)

# 設定參數4, 5: 參數4為設定chromedriver所在位置，注意: chromedriver必須對應電腦安裝之chrome的版本，如果版本不符請至網站下載新版本，本篇使用86版。參數5為爬資料的目標網頁。

browser = webdriver.Chrome('C:/Users/user/Desktop/crawl/tool/chromedriver_86.exe') # 設置chromedriver的位置
browser.get('http://www.airitilibrary.com/') # 開啟chromedriver，連到目標網頁



# 間格時間，避免跳太快導致錯誤
time.sleep(3)



# 1.進入並解析網頁
# 1-1.模擬人為操作
browser.find_element_by_link_text("進階檢索").click()
time.sleep(2)
browser.find_element_by_id("editAlg").click()
browser.find_element_by_id("Clear").click()
browser.find_element_by_id("inquiryCondition").clear()
browser.find_element_by_id("inquiryCondition").send_keys(search_name) #輸入要查詢的條件
browser.find_element_by_id("PageSize50").click()
browser.find_element_by_id("AdvancedResearchSubmit").click()

#間格時間，避免避免跳太快導致錯誤
time.sleep(3)

# 輸出日期
print('搜尋時間： ' + time.strftime("%y/%m/%d") + ' ' + time.strftime("%H:%M:%S"))

# # 1-2.自定函數_檢查頁數(此處為非必要)
# def checkPage(category):
#     browser.find_element_by_id(category).click()  #點選會議論文
#     time.sleep(3)  #休息3秒
#     soup = BeautifulSoup(browser.page_source, 'lxml')  #解析網頁
#     page_str = soup.find('div', {'class': 'txt1'})
#     time.sleep(3)
#     page_text = page_str.text
#     pattern = '[0-9]+'
#     page_re = re.findall(pattern, page_text)[0]  # 利用正規表達式抓出文字串的數字
#     page_int = int(page_re)
#
#     if page_int == 0:
#         print(category)
#         print('共 0 筆')
#         print('...........分隔線..........')
#     else:
#
#         page_all = (page_int // 50) + 1
#         page_last = page_int % 50
#         print(category)
#         print('共 '+ str(page_int) +' 筆')
#         print('有 '+ str(page_all) +' 頁')
#         print('最後一頁剩 '+ str(page_last) +' 筆')
#         print('...........分隔線..........')
#
# # 取得總頁數，計算要點幾次，以及最後一次剩幾筆_期刊文章、會議論文、碩博士論文、電子書
# checkPage('期刊文章')
# checkPage('會議論文')
# checkPage('碩博士論文')
# checkPage('電子書')



# 2.抓取頁面資訊
def crawlerPage(num, category, pName): # 2-1.先進入頁面
    browser.find_element_by_id(category).click()  #點選會議論文
    time.sleep(3)  #休息3秒
    soup = BeautifulSoup(browser.page_source, 'lxml')
    # 2-2.判斷這個頁面的資料數量(如果沒有資料，就會進入2-3-1)
    page_str = soup.find('div', {'class': 'txt1'})
    page_text = page_str.text
    pattern = '[0-9]+'
    page_re = re.findall(pattern, page_text)[0]  # 利用正規表達式抓出文字串的數字
    page_int = int(page_re) #當前共有幾筆資料

    if page_int == 0: # 2-3-1.發現當前頁面沒有資料
        print(category)
        print('共 0 筆')
        print('...........分隔線..........')
    else: # 2-3-2.發現當前頁面有資料
        browser.find_element_by_id("sel_v").click()  #點開頁數
        time.sleep(1)
        browser.find_element_by_id("sel_sec_e").click()  #選50頁
        time.sleep(1)
        # 2-4.判斷這個頁面的頁數有多少
        page_str = soup.find('div', {'class':'txt1'})
        page_text = page_str.text
        pattern = '[0-9]+'
        page_re = re.findall(pattern, page_text)[0]  #利用正規表達式抓出文字串的數字
        page_int = int(page_re) #當前共有幾筆資料
        page_all = (page_int // 50) + 1 #當前共有幾頁資料
        print(category)
        print('總筆數' + str(page_int))
        page = 1
        i = 1
        while page <= page_all:
            soup = BeautifulSoup(browser.page_source, 'lxml')
            page_len = soup.find_all('td', {"class":"titleB"})
            print('頁筆數' + str(len(page_len)))
            pName_list_title = []  # 創一新list (title)
            pName_list_Author = [] #創一新list (作者)
            pName_list_source = [] #創一新list (來源與時間)
            current = 0  # 從0開始作者名稱list
            for current in range(len(page_len)):
                pName_text_title = soup.find_all('', {"class":"titleB"})[current].find('a').text #抓取著作標題
                pName_list_title.append(pName_text_title)

                pName_text_Author = soup.find_all('', {"class": "titleB"})[current].find_all('p')[1].text #抓作者名稱
                pName_list_Author.append(pName_text_Author)

                pName_text_source = soup.find_all('', {"class": "titleB"})[current].find_all('p')[2].text #抓取出處與時間
                pName_list_source.append(pName_text_source)

            # 抓出所有資訊(一次全部抓取)
            pName_all = [tag.text for tag in soup.find_all('td', {"class":"titleB"})]
            print('抓取筆數' + str(len(pName_all)))

            #定義一個儲存成csv的函數
            def save_file(pName_list_title, pName_list_Author, pName_list_source, pName_all):

                # title欄位轉成dataframe
                pName_list_title_df = pd.DataFrame(pName_list_title)
                pName_list_title_df.columns = ["title"]
                pName_list_title_df = pName_list_title_df.loc[:, "title"].str.replace('\n', '').replace('\r','')  # 修正資料

                # 作者欄位轉成dataframe
                pName_list_author_df = pd.DataFrame(pName_list_Author)
                pName_list_author_df.columns = ["author"]
                pName_list_author_df = pName_list_author_df.loc[:, "author"].str.replace('\n', '').replace('\r','')  # 修正資料

                # 來源欄位轉成dataframe
                pName_list_source_df = pd.DataFrame(pName_list_source)
                pName_list_source_df.columns = ["source"]
                pName_list_source_df = pName_list_source_df.loc[:, "source"].str.replace('\n', '').replace('\r','') # 修正資料

                # all欄位轉成dataframe
                pName_all_df = pd.DataFrame(pName_all)
                pName_all_df.columns = ["all"]
                pName_all_df = pName_all_df.loc[:, 'all'].str.replace('\n', ' ').replace('\r',' ')  # 修正資料


                # 合併欄位成csv檔
                pName_merge = pd.concat([pName_list_title_df, pName_list_author_df, pName_list_source_df, pName_all_df], axis=1)
                pName_merge['system'] = datasource  # 加上搜尋來源
                pName_merge['category'] = category  # 加上文章類別
                pName_merge['cluster'] = pName  # 加上叢集名稱
                pName_merge.to_csv('{}_{}_{}.csv'.format(pName, num, i), sep=',', encoding='utf-8', header=None)  # 存成csv

            # 2-5-1.如果已經到了最後一個頁面
            if page == page_all:
                save_file(pName_list_title, pName_list_Author, pName_list_source, pName_all) #將變數帶入savefile函數
                page = page + 1
                i = i + 1
            # 2-5-2.如果還有頁面要儲存
            else:
                save_file(pName_list_title, pName_list_Author, pName_list_source, pName_all) #將變數帶入savefile函數
                browser.find_element_by_id("imgNext").click()  #按下一頁
                time.sleep(3)
                page = page + 1
                i = i + 1
        print('...........分隔線..........')


# 抓取頁面資訊_期刊文章、會議論文、碩博士論文、電子書
crawlerPage(1, '期刊文章', pName)
crawlerPage(2, '會議論文', pName)
crawlerPage(3, '碩博士論文', pName)
crawlerPage(4, '電子書', pName)

browser.close()  #關閉瀏覽器




# 3.將csv合併

with open('{}_main.csv'.format(pName), 'a', encoding='utf-8') as singleFile:
    for csv in glob('{}_*.csv'.format(pName)):
        if csv == '{}_main.csv'.format(pName):
            pass
        else:
            for line in open(csv, 'r', encoding='utf-8'):
                singleFile.write(line)
