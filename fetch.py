import re
from datetime import datetime

import requests as rq
from pyquery import PyQuery as pq


class Just(object):
    # 请求头
    REQUEST_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    # 登陆教务url
    LOGIN_URL = 'http://jwgl.just.edu.cn:8080/jsxsd/xk/LoginToXk'

    # 获取绩点url
    GRADE_URL = 'http://jwgl.just.edu.cn:8080/jsxsd/kscj/cjcx_list'

    # 获取教室url
    CLASS_URL = 'http://jwgl.just.edu.cn:8080/jsxsd/kbcx/kbxx_classroom_ifr'

    # 获取校区教学楼url
    BUILDING_URL = 'http://jwgl.just.edu.cn:8080/jsxsd/kbcx/getJxlByAjax'

    # 校区代号
    CAMPUS_ID = {'东校区': '01', '南校区': '02', '西校区': '03', '张家港校区': '04', '苏州理工校区': '05'}

    # 节次代号
    LESSON_ID = ['上午第一大节', '上午第二大节', '下午第一大节', '下午第二大节', '晚上第一大节']

    def __init__(self, user_name: str, pass_word: str) -> None:
        self.user_name = user_name
        self.__pass_word = pass_word

        self.__seq_req = rq.session()

    def login(self) -> bool:
        form = {'USERNAME': self.user_name, 'PASSWORD': self.__pass_word}
        res = self.__seq_req.post(self.LOGIN_URL, data=form, headers=self.REQUEST_HEADER)
        res.raise_for_status()
        # 出错页面与登陆成功页面编码不同
        res.encoding = res.apparent_encoding
        text = res.text
        # print(text)
        if '用户名或密码错误' in text:
            print('用户名或密码错误')
            return False

        elif '用户名或密码不能为空' in text:
            print('用户名或密码不能为空')
            return False

        else:
            print('教务系统登录成功')
            return True

    def get_grade(self, date: str) -> []:
        """
        获取指定日期成绩
        :param date: xxxx-xxxx-1,2
        :return:
        """
        # 判断date是否合法
        if re.match(r'[2-9]\d{3}-2\d{3}-[12]', date):
            year1, year2, term = date.split('-')
            if int(year1) + 1 != int(year2):
                print(date + '不合法')
                return
        else:
            print(date + '不合法')
            return

        form = {'kksj': date, 'kcxz': None, 'kcmc': '', 'xsfs': 'all'}
        res = self.__seq_req.post(self.GRADE_URL, headers=self.REQUEST_HEADER, data=form)
        res.raise_for_status()
        res.encoding = 'UTF-8'
        # 解析成绩
        grades = []
        doc = pq(res.text)
        trs = doc('#dataList').items('tr')
        next(trs)
        for tr in trs:
            grade = {}
            tds = tr.children('td')
            # 课程号，课程名称，成绩，学分，考核方式，课程属性，课程性质
            grade['index'] = tds[2].text
            grade['name'] = tds[3].text
            grade['mark'] = tds[4].text
            grade['credit'] = tds[5].text
            grade['method'] = tds[7].text
            grade['attribute'] = tds[8].text
            grade['property'] = tds[9].text
            # 替代课程无法得知学分
            if grade['credit'] is None:
                grade['property'] = '课程被替代'
            grades.append(grade)
        return grades

    def get_class_room(self, start_date: str, now_date: str = None, xq: str = None, jzw: str = None) -> dict:
        """
        空教室查询
        :param jzw: 校区：东校区，南校区，西校区，张家港校区，苏州理工校区
        :param xq: 教学楼
        :param start_date: 当前学期开始时间 xxxx-xx-xx
        :param now_date: 查询时间 xxxx-xx-xx
        :return:
        """
        # todo: 这里有一个异常
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        # 确定学年，周数，星期
        year = start_date.year
        month = start_date.month
        if month < 6:
            term = '{start}-{end}-{index}'.format(start=year - 1, end=year, index=2)
        else:
            term = '{start}-{end}-{index}'.format(start=year, end=year + 1, index=1)
        if not now_date:
            now_date = datetime.today()
        else:
            # todo: 这里有一个异常
            now_date = datetime.strptime(now_date, '%Y-%m-%d')
        week_label = now_date.weekday()
        week_index = (now_date - start_date).days // 7 + 1

        buildings = None
        if xq:
            xq = xq.replace('苏理', '苏州理工')
            result = self.CAMPUS_ID.get(xq, None)
            if result:
                xq = result
                # 获取教学楼
                res = self.__seq_req.post(self.BUILDING_URL, headers=self.REQUEST_HEADER, data={'xqid': xq})
                res.raise_for_status()
                res.encoding = 'utf-8'
                buildings = {item['dmmc']: item['dm'] for item in res.json()}
            else:
                print('未找到校区' + xq)
                return

        if jzw and buildings:
            jzw = jzw.upper()
            result = buildings.get(jzw, None)
            if result:
                jzw = result
            else:
                print('未找到教学楼' + jzw)
                return

        form = {'xnxqh': term,
                'skyx': '',
                'xqid': xq,
                'jzwid': jzw,
                'zc1': week_index,
                'zc2': week_index,
                'jc1': '',
                'jc2': '', }
        res = self.__seq_req.post(self.CLASS_URL, headers=self.REQUEST_HEADER, data=form)
        res.raise_for_status()
        res.encoding = 'utf-8'
        # 解析表格
        empty = {}
        doc = pq(res.text)
        trs = doc('#kbtable').items('tr')
        next(trs)
        next(trs)
        for tr in trs:
            tds = tr.children('td')
            class_name = tds[0].find('nobr').text
            class_empty_list = []
            empty[class_name] = class_empty_list
            for i, td in enumerate(tds[week_label * 5 + 1:week_label * 5 + 6]):
                if not td.cssselect('div'):
                    class_empty_list.append(self.LESSON_ID[i])
        return empty
