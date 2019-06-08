import re
import warnings
from argparse import ArgumentParser

import requests as rq

from config import user_name, password, start_date, password_
from fetch import Just
from process import class_print, table_print, calculate

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    parser = ArgumentParser(description='轻松获取just教务信息')
    subparsers = parser.add_subparsers(dest='command', description='command', required=True)

    grade_parser = subparsers.add_parser('grade', help='获取绩点信息')
    grade_parser.add_argument('date', type=str)
    grade_parser.add_argument('-detail', type=bool, default=False, help='是否打印详细信息')

    class_parser = subparsers.add_parser('class', help='获取空教室信息')
    class_parser.add_argument('-date', type=str, default=None, help='查询日期')
    class_parser.add_argument('-xq', type=str, default=None, help='校区')
    class_parser.add_argument('-jzw', type=str, default=None, help='教学楼')

    args = vars(parser.parse_args())
    just = Just(user_name, password, password_)
    # 网络有问题时，使用校园vpn
    try:
        just.login()
    except (rq.exceptions.ConnectionError, rq.exceptions.ConnectTimeout):
        just.enable_vpn()
        just.login()

    if args['command'] == 'grade':
        date = args['date']
        # 判断date是否合法
        if re.match(r'[2-9]\d{3}-2\d{3}-[12]', date):
            grades = just.get_grade(date)
            print(date + '平均绩点：' + str(calculate(grades)))
            if args['detail']:
                table_print(grades)
        elif re.match(r'[2-9]\d{3}-2\d{3}', date):
            year1, year2 = date.split('-')
            if int(year1) >= int(year2):
                raise RuntimeError(date + '日期不合法')
            else:
                # xxxx-xxxx的绩点计算
                times = []
                all_grades = []
                term = 1
                start = int(year1)
                for i in range((int(year2) - int(year1)) * 2):
                    times.append('{start}-{end}-{term}'.format(start=start, end=start + 1, term=term))
                    all_grades.append(just.get_grade(times[i]))
                    if term == 2:
                        start += 1
                        term = 1
                    else:
                        term = 2
                print(date + '平均绩点：' + str(calculate(sum(all_grades, []))))
                print()
                for i, time in enumerate(times):
                    print(time + '平均绩点：' + str(calculate(all_grades[i])))
                    if args['detail']:
                        table_print(all_grades[i])
                    print()
        else:
            raise RuntimeError(date + '日期不合法')
    elif args['command'] == 'class':
        class_print(just.get_class_room(start_date=start_date, now_date=args['date'], xq=args['xq'], jzw=args['jzw']))
