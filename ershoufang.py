#coding=utf-8
import time
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
# from pyquery import PyQuery as pq
global sleeptime
sleeptime = 5
global browser
time_count = 0
empty_count = 0
class Crawler:
    def __init__(self,browser,url,xiaoqu_name,fp_out):
        self.url = url
        self.xiaoqu_name = xiaoqu_name
        self.browser = browser
        self.browser.get(self.url)
        self.output = []
        self.mean_price = ["None"]
        self.price_list = []
        self.area_list = []
        self.fp_out = fp_out
        self.empty_flag = False
        self.info_dict = {}
        self.soup = 0

    def craw_main(self):
        try:
            print self.xiaoqu_name,
            print " 爬虫中"
            self.browser.find_element_by_id('input_keyw1').send_keys(self.xiaoqu_name.decode('utf-8', 'ignore'))
            self.browser.find_element_by_id('esf_B01_32').click()
            time.sleep(2*sleeptime)
            html = self.browser.page_source
            self.soup = BeautifulSoup(html, 'html.parser')
            if self.__is_empty():
                self.empty_flag = True
                print self.xiaoqu_name,
                print " 无法找到匹配"
                self.__output()
                global empty_count
                empty_count += 1
                return
            junjias = self.soup.select('p.mt12')
            if len(junjias) > 0:
                junjia_text = junjias[0].get_text()
                num_re = re.compile(r"\d+")
                price_list = num_re.findall(junjia_text)
                if len(price_list) > 0:
                    price = int(num_re.findall(junjia_text)[0])
                    self.mean_price = [price]
            self.ana_house()
            while self.__if_next():
                self.ana_house()
            self.__output()
        except Exception, e:
            print Exception, ":", e

    def __is_empty(self):
        # flag = False
        # flag1 = True
        # # 查看要查的小区是否有租房信息
        # searchNones = self.soup.select('div.searchNone')
        # if len(searchNones) < 1:
        #     flag1 = False
        # if flag1 and "您可能对以下房源感兴趣" in searchNones[0].get_text():
        #     flag = False
        # searchNones = self.soup.select('div.sorry_word')
        # flag1 = True
        # if len(searchNones) < 1:
        #     flag1 = False
        # if flag1 and "很抱歉" in searchNones[0].get_text():
        #     flag = True
        # return flag
        text = self.soup.get_text()
        if "很抱歉" in text:
            return True
        else :
            return False



    def __if_next(self):
        # 查看是否有下一页，是否需要分页
        fanye_infos = self.soup.select('div.fanye')
        fanye_info = fanye_infos[0]
        fanye_contents = fanye_infos[0].contents
        if "下一页" in fanye_info.get_text():

            for con in fanye_contents:
                if type(con) != type(fanye_info):
                    continue
                if "下一页" in con.get_text():
                    print self.xiaoqu_name,
                    print "翻页"
                    home_url = str(browser.current_url)
                    par = home_url.index('.com')
                    url_add = con.attrs["href"]
                    while url_add[0]=='/':
                        url_add = url_add[1:]
                    url = home_url[:par+5] + url_add
                    self.browser.get(url)
                    time.sleep(sleeptime)
                    html = self.browser.page_source
                    self.soup = BeautifulSoup(html, 'html.parser')
            return True
        else:
            return False

    def ana_house(self):
        infos = self.soup.select('dd.info')
        # print infos
        for info in infos:
            # title = info.find("p","title")
            # a = title.find("a")
            # print type(title.get_text())
            # print a.attrs['title']
            c = info.find("p", class_="mt12")
            area_Tag = info.select("div.area")
            num_re = re.compile("\d+")
            area_re_list = num_re.findall(area_Tag[0].get_text())
            area_vle = float(area_re_list[0])
            price_Tag = info.select('span.price')[0]
            price_vle = float(price_Tag.get_text())
            self.price_list.append(price_vle)
            self.area_list.append(area_vle)
            if type(c) != type(None):
                house_info = c.get_text().strip().split('|')
                if house_info[0][:2] not in self.info_dict:
                    self.info_dict[house_info[0][:2]] = {"area":[],"price":[]}

                dict3 = self.info_dict[house_info[0][:2]]
                dict3["area"].append(area_vle)
                dict3["price"].append(price_vle)

    def __sta_fangxing(self):
        self.fang_xing_shu_liang = []
        for key in self.info_dict:
            self.fang_xing_shu_liang.append((key,len(self.info_dict[key]["area"])))
        self.fang_xing_shu_liang = sorted(self.fang_xing_shu_liang,key=lambda x: -x[1])
        if len(self.fang_xing_shu_liang) < 4:
            for i in range(4 -len(self.fang_xing_shu_liang)):
                self.fang_xing_shu_liang.append(["None",0])

    def __output(self):
        line = [self.xiaoqu_name]
        if self.empty_flag:
            self.__output_line(line)
            return
        line.append(np.min(self.area_list))
        line.append(np.max(self.area_list))
        line.append(np.min(self.price_list))
        line.append(np.max(self.price_list))
        line.append(len(self.area_list))
        self.__sta_fangxing()
        line.extend(self.mean_price)
        for i in range(4):
            line.extend(self.fang_xing_shu_liang[i])
        self.__output_line(line)
        global time_count
        time_count +=1
        print line

    def __output_line(self,line):
        index = 0
        for w in line:
            if index == 0:
                self.fp_out.write(str(w))
            else:
                self.fp_out.write(',' + str(w))
            index += 1
        self.fp_out.write('\n')

def zufang_main(file_in,file_out):
    global browser
    global time_count
    browser = webdriver.Chrome()
    fp_in = open(file_in, "r")
    fp_out = open(file_out, "w")
    lines = fp_in.readlines()
    for line in lines:
        print line
        if "物业名称" in line:
            continue
        line = line.strip()
        list_line = line.split(',')
        crawler = Crawler(browser,"http://esf.sh.fang.com/",list_line[0], fp_out)
        crawler.craw_main()


    fp_in.close()
    fp_out.close()
    browser.close()
    print "共计 ",
    print time_count
    print "成功 ",
    print empty_count

zufang_main("houselist(1).csv","ershoufanginfo.csv")

def zufang_test(file_in,file_out):
    global browser
    browser = webdriver.Chrome()
    fp_out = open(file_out, "w")
    lists = ["证大家园酒店式公寓"]
    for name in lists:
        crawler = Crawler(browser,"http://esf.sh.fang.com/",name, fp_out)
        crawler.craw_main()


    fp_out.close()
    browser.close()

# zufang_test("houselist(1).csv","zufanginfo.csv")