#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 7/27/17 9:08 AM
# @Author  : WZX
# @Site    : 
# @File    : login.py
# @Software: PyCharm
# function : 登录江科大强智科技,教务系统,保存cookie,用seq_requests做其他操作
import os

import requests
from PIL import Image

from config import user_name, password

# 登录界面url
login_url = 'http://jwgl.just.edu.cn:8080/'

# 获取加密码,发送表单的url
url = 'http://jwgl.just.edu.cn:8080/Logon.do'

# 获取验证码的url
verify_url = 'http://jwgl.just.edu.cn:8080/verifycode.servlet'

# 请求头
kv = {'Host': 'jwgl.just.edu.cn:8080',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0', }

# 保存cookie的会话
seq_requests = requests.session()


# 返回加密的用户名和密码
def encrypt(user, pass_word, scode, sxh):
    code = user + '%%%' + pass_word
    encoded = ''
    for i in range(len(code)):
        if i < 20:
            encoded = encoded + code[i:i + 1] + scode[0:int(sxh[i: i + 1])]
            scode = scode[int(sxh[i:i + 1]): len(scode)]
        else:
            encoded = encoded + code[i: len(code)]
            i = len(code)
    return encoded[0:len(encoded) - 10]


# 获取加密码
def get_code():
    data = {'method': 'logon', 'flag': 'sess'}
    try:
        res = seq_requests.post(url, params=data, headers=kv, timeout=3)
        # print(res.headers)
        # res.encoding = 'utf-8'
        text = res.text
        res.raise_for_status()
        # print(text)
        scode = text.split('#')[0]
        sxh = text.split('#')[1]
        return [scode, sxh]
    except:
        print('网络问题,程序中断')
        os._exit(0)


# 处理验证码
def handle_verify_code():
    try:
        res = seq_requests.get(verify_url, headers=kv, timeout=3)
        res.raise_for_status()
        # 保存验证码到temp文件
        with open('temp', 'wb') as file:
            file.write(res.content)
        # 打开图片,人工识别
        with Image.open('temp') as im:
            im.show()
            yanZ = input('根据图片请输入验证码')

            # 若验证码输入错误,过多的图片窗口可能影响判断
            print('请关闭图片')
            input('任意键继续')
        return yanZ
    except:
        print('网络问题,程序中断')
        os._exit(0)


def login():
    try:
        seq_requests.get(login_url, headers=kv, timeout=3)
        # 是否登录成功
        flag = False
        while flag is False:
            yanZ = handle_verify_code()
            code = get_code()
            encode = encrypt(user_name, password, code[0], code[1])
            form = {'useDogCode': '', 'encoded': encode, 'RANDOMCODE': yanZ}
            data = {'method': 'logon'}
            res = seq_requests.post(url, params=data, headers=kv, data=form, timeout=3)
            res.encoding = 'utf-8'
            res.raise_for_status()
            text = res.text
            if text.__contains__('该帐号不存在或密码错误'):
                print('该帐号不存在或密码错误')
                os._exit(0)
            if text.__contains__('验证码错误!!'):
                print('验证码错误')
            else:
                flag = True
                # print(text)
                print('登录成功,正在跳转')
    except:
        print('网络问题,程序中断')
        os._exit(0)


if __name__ == '__main__':
    login()
