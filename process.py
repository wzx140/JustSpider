from prettytable import PrettyTable

# 五分制转化为绩点
five_to_grade = {'优': 4.5, '良': 3.5, '中': 2.5, '及格': 1.5, '不及格': 0}


def calculate(grades: list) -> float:
    """
    计算绩点,任选不计入绩点
    :param grades:
    :return:
    """
    grade_sum = 0
    credit_sum = 0
    cal_list = [grade for grade in grades if
                grade['attribute'] != '任选' and '体育' not in grade['name'] and grade['credit']]
    for grade in cal_list:
        mark = grade['mark']
        if mark == '通过':
        	# 跳过大学生体测
        	continue
        credit = float(grade['credit'])
        credit_sum += credit
        if mark.isdigit():
            if int(mark) <= 60:
                grade_sum += 0
            else:
                grade_sum += (int(mark) / 10 - 5) * float(credit)
        else:
            grade_sum += five_to_grade[mark] * float(credit)
    return round(grade_sum / credit_sum, 3)


def table_print(grades: list) -> None:
    """
    成绩表格打印
    :param grades:
    :return:
    """
    table = PrettyTable(['课程号', '课程名称', '成绩', '学分', '考核方式', '课程属性', '课程性质'])
    for grade in grades:
        table.add_row(
            [grade['index'], grade['name'], grade['mark'], grade['credit'], grade['method'], grade['attribute'],
             grade['property']])
    print(table)


def class_print(empty: dict) -> None:
    for class_ in empty.keys():
        lessons = empty[class_]
        if lessons:
            lessons = str(lessons).lstrip('[').rstrip(']').replace("'", '')
            print(class_ + '：' + lessons)
