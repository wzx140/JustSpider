#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 7/27/17 7:12 PM
# @Author  : WZX
# @Site    : 
# @File    : jiDian.py
# @Software: PyCharm
# function : 算出学分绩点,基于login模块
import sys

from bs4 import BeautifulSoup

from config import five_to_grade, time
from login import kv, seq_requests, login

url_query = 'http://jwgl.just.edu.cn:8080/jsxsd/kscj/cjcx_list'


# 获得制定学期的成绩页面
def get_grade_html():
    form = {'kksj': time, 'kcxz': '', 'kcmc': '', 'xsfs': 'all'}
    try:
        res = seq_requests.post(url_query, headers=kv, data=form)
        res.raise_for_status()
        res.encoding = 'utf-8'
        return res.text
    except:
        print('网络问题,程序中断')
        sys.exit(0)


# 获取成绩
def get_grade_item(html):
    soup = BeautifulSoup(html, 'lxml')
    # print(html)
    trs = soup.find_all('tr')[2:]
    grade_list = []
    for tr in trs:
        # print(tr)
        tds = tr.find_all('td')
        index = tds[2].text
        name = tds[3].text
        grade = tds[4].text
        xue_fen = tds[5].text
        kao_he = tds[7].text
        atr = tds[8].text
        grades = [index, name, grade, xue_fen, kao_he, atr]
        grade_list.append(grades)
    return grade_list


# 计算绩点
def calculate(grade_list):
    grade_sum = 0
    xue_fen_sum = 0
    cal_list = [i for i in grade_list if not i[5] == '任选' and not str(i[1]).__contains__('体育')]
    for i in cal_list:
        # print(i)
        xue_fen_sum += float(i[3])
        if i[2].isdigit():
            if int(i[2]) <= 60:
                grade_sum += 0
            else:
                grade_sum += (int(i[2]) / 10 - 5) * float(i[3])
        else:
            grade_sum += five_to_grade[i[2]] * float(i[3])
    return grade_sum / xue_fen_sum


if __name__ == '__main__':
    login()
    html = get_grade_html()
    grade_list = get_grade_item(html)
    ji_dian = calculate(grade_list)
    print('你', time, '平均绩点为', ji_dian)
    print('按任意键退出')
