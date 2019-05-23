from urllib.parse import urlparse

import requests
from pyquery import PyQuery as pq


class Vpn(object):
    # 登录vpn url
    LOGIN_URL = 'https://vpn.just.edu.cn/dana-na/auth/url_default/login.cgi'

    # 请求头
    REQUEST_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    # 转化url
    VPN_URL = 'https://vpn.just.edu.cn{path},DanaInfo={domain},Port={port}'

    def __init__(self, user_name, password, seq_req: requests.sessions.Session) -> None:
        self.__user_name = user_name
        self.__password = password
        self.__seq_req = seq_req

    def login(self):
        form = {'username': self.__user_name, 'password': self.__password, 'realm': 'LDAP-REALM'}
        res = self.__seq_req.post(self.LOGIN_URL, data=form, headers=self.REQUEST_HEADER, verify=False)
        res.raise_for_status()
        if 'failed' in res.url:
            raise RuntimeError('用户名或密码错误')
        elif 'https://vpn.just.edu.cn/dana/home/starter.cgi' in res.url:
            print('登录成功')
        elif 'user-confirm' in res.url:
            # 继续会话
            res.encoding = 'utf-8'
            doc = pq(res.text)
            form_data = doc('#DSIDFormDataStr').attr('value')
            form = {'btnContinue': '继续会话', 'FormDataStr': form_data}
            res = self.__seq_req.post('https://vpn.just.edu.cn/dana-na/auth/url_default/login.cgi',
                                      headers=self.REQUEST_HEADER, data=form)
            if 'check=yes' in res.url:
                print('登录成功')
            else:
                raise RuntimeError('请手动退出会话')
        else:
            raise RuntimeError('未知错误，登录失败')

    def get_session(self):
        return self.__seq_req

    def request(self, url: str, method: str, data: dict = None):
        """
        请求
        :param method: post or get
        :param url:
        :return:
        """
        # 转化url
        result = urlparse(url)
        port = result.port
        if result.port is None:
            port = 80
        path = result.path
        if result.query:
            path = path + '?' + result.query
        if result.params:
            path = path + ';' + result.params
        if result.fragment:
            path = path + '#' + result.fragment
        vpn_url = self.VPN_URL.format(domain=result.hostname, path=path, port=port)

        if method == 'get':
            res = self.__seq_req.get(vpn_url, headers=self.REQUEST_HEADER)
        elif method == 'post':
            res = self.__seq_req.post(vpn_url, headers=self.REQUEST_HEADER, data=data)
        else:
            raise RuntimeError('非法请求')

        # 处理不信任证书问题
        res.raise_for_status()
        res.encoding = 'utf-8'
        if 'invalidsslsite_confirm' in res.url:
            doc = pq(res.text)
            xsauth = doc('#xsauth_400').attr('value')
            url = doc('#url_9').attr('value')
            certHost = doc('#certHost_2').attr('value')
            certPort = doc('#certPort_2').attr('value')
            certDigest = doc('#certDigest_2').attr('value')
            errorCount = doc('#errorCount_2').attr('value')
            notAfter = doc('#notAfter_2').attr('value')
            form = {'xsauth': xsauth, 'url': url, 'certHost': certHost, 'certPort': certPort, 'certDigest': certDigest,
                    'errorCount': errorCount, 'notAfter': notAfter, 'action': '继续'}
            res = self.__seq_req.post('https://vpn.just.edu.cn/dana/home/invalidsslsite_confirm.cgi',
                                      headers=self.REQUEST_HEADER, data=form)
        return res
