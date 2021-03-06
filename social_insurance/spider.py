#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2017/11/4 上午9:26
# @Author  : fanqiang
# @Site    : 
# @File    : spider.py
# @Software: PyCharm

import hashlib
import pathlib
import re
import subprocess
import time
from datetime import datetime

import requests
from PIL import Image, ImageEnhance
from prettytable import PrettyTable
from pytesseract import pytesseract

_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/61.0.3163.100 Safari/537.36"
        }

_operators = {"加": "+", "减": "-", "除以": "/", "乘": "*"}

_module_path = pathlib.Path(__file__).parent


def recognition_identify(filepath):
    """ 根据传入图片别验证码 """
    img = Image.open(filepath)
    path = pathlib.Path(filepath)
    # 对比度增强
    sharpness = ImageEnhance.Contrast(img.convert('L'))
    sharp_img = sharpness.enhance(2.0)
    sharp_img.save(str(path.parent) + "/identify_converted.jpeg")
    identify_code = pytesseract.image_to_string(sharp_img)
    return identify_code


def answer_problem(problem):
    """ 回答问题 """
    problem_context = re.findall(r'(\d+)(\w+)(\d+)', problem)[0]
    expression = '%s%s%s' % (problem_context[0], _operators[problem_context[1]], problem_context[2])
    return int(eval(expression))


def md5_encrypt(password):
    """ 使用md5 加密 """
    m2 = hashlib.md5()
    m2.update(password.encode('utf-8'))
    return m2.hexdigest()


# social  Insurance

class SipSocialInsuranceSpider(object):
    """
        苏州工业园区社保缴费记录查询
    """
    def __init__(self, username, password):
        self._userName = username
        self._uPassword = password
        self._session = None
        self._session_id = None
        self._token = None

    # 登陆
    def login(self):
        """ 执行登录动作并设置cookies """
        self._init_session()

        retry = 0
        while True:
            # 获取验证码
            identify_path = self._fetch_identify()
            identify = recognition_identify(identify_path)

            # 回答问题
            problem = self._fetch_problem()
            answer = answer_problem(problem)

            # 获取rsa key
            rsa = self._fetch_rsa_param()
            rsa_param = self._generate_rsa_params(rsa)

            # 尝试登陆
            token = self._try_login(identify, answer, rsa_param)

            if token.startswith("shwq"):
                print("用户%s登陆成功:%s" % (self._userName, token))
                self._token = token
                self._set_login_success_cookies()
                return token
            elif retry <= 10:
                print("用户%s第%s尝试登陆失败:%s" % (self._userName, retry, token))
                retry += 1
                time.sleep(1)
                continue
            else:
                print("用户%s第%s尝试登陆失败,超出重试次数:%s" % (self._userName, retry, token))
                break

    # 初始化cookies
    def _init_session(self):
        self._session = requests.session()
        res = self._session.post("https://www.sipspf.org.cn/person_online/emp/loginend.jsp", headers=_headers)
        self._session_id = res.cookies.get("JSESSIONID")

    # 尝试登陆
    def _try_login(self, identify, answer, rsa_param):
        payloads = {
            "uname": self._userName,
            "upass": md5_encrypt(self._uPassword),
            "sessionid": self._session_id,
            "identify": identify,
            "answer": answer,
            "param3": rsa_param
        }

        _headers['Origin'] = "https://www.sipspf.org.cn"
        _headers['X-Requested-With'] = "XMLHttpRequest"
        _headers['Content-Type'] = "application/x-www-form-urlencoded"
        _headers['Referer'] = "https://www.sipspf.org.cn/person_online/emp/loginend.jsp"
        wqcall = self._session.post('https://www.sipspf.org.cn/person_online/service/EMPLogin/login?wqcall=%s' %
                                    int(time.time()), data=payloads, headers=_headers)
        wqcall.encoding = 'utf-8'
        emkey = wqcall.text
        return emkey

    # 设置登陆成功的cookies
    def _set_login_success_cookies(self):
        jar = self._session.cookies
        jar.set('EmpRegKey', self._token, domain='www.sipspf.org.cn', path='/')
        jar.set('ERKey', self._token, domain='www.sipspf.org.cn', path='/')
        jar.set('LoginType', '1', domain='www.sipspf.org.cn', path='/')
        jar.set(self._token, str(int(time.time())), domain='www.sipspf.org.cn', path='/')

    # 获取社保验证码
    def _fetch_identify(self):
        _headers['Accept'] = 'image/webp,image/apng,image/*,*/*;q=0.8'
        identify = self._session.post('https://www.sipspf.org.cn/person_online/service/identify.do?sessionid=%s'
                                       '&random=%s' % (self._session_id, int(time.time())), headers=_headers)

        md5_dir = 'captcha/sipss/' + md5_encrypt(self._session_id)

        path = pathlib.Path(md5_dir)
        if not path.exists():
            path.mkdir(parents=True)

        identify_path = md5_dir + "/identify.jpeg"

        with open(identify_path, 'wb') as file:
            file.write(identify.content)
        return str(path.absolute()) + '/identify.jpeg'

    # 获取登陆问题
    def _fetch_problem(self):
        _headers['Accept'] = '*/*'
        _headers['Referer'] = 'https://www.sipspf.org.cn/person_online/emp/loginend.jsp'
        _headers['X-Requested-With'] = 'XMLHttpRequest'
        problem = self._session.post('https://www.sipspf.org.cn/person_online/service/problem.do?'
                                      'sessionid=%s&random=%s' % (self._session_id, int(time.time())), headers=_headers)
        problem.encoding = 'utf-8'
        return problem.text

    # 获取rsa加密参数
    def _fetch_rsa_param(self):
        param = self._session.post('https://www.sipspf.org.cn/person_online/service/EMPLogin/param?'
                                    'sessionid=%s&random=%s' % (self._session_id, int(time.time())), headers=_headers)
        param.encoding = 'utf-8'
        rsa = param.text.split(":")
        return rsa

    # 生成rsa加密后的参数
    def _generate_rsa_params(self, rsa_params):

        command = 'node %s/security.js %s %s %s %s' % (str(_module_path.absolute()), rsa_params[1], self._userName,
                                                       rsa_params[0], self._uPassword)
        # print(command)
        param3call = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        param3 = str(param3call.stdout.readline(), encoding='utf-8').strip()
        return param3

    def fetch_records(self):
        """ 获取社保缴费记录 """
        _headers["Accept"] = "application/json, text/javascript, */*"
        _headers["X-Requested-With"] = "XMLHttpRequest"

        account_query = self._session.post('https://www.sipspf.org.cn/person_online/account/accountQuery?'
                                            'regkey=%s&itype=1' % self._token, headers=_headers)
        account_query.encoding = 'utf-8'
        return SocialInsuranceRecords(self._userName, account_query.json())


class SocialInsuranceRecords(object):
    """
        用于表示社保查询结果的类
    """
    def __init__(self, username, records):
        self.__username = username
        self.__records = [record for record in records if '正常工资1' == record['renderType']]

    def pretty(self):
        """ 返回一个格式化输出 PrettyTable对象 """

        print_head = "月 缴费类型 缴费基数 入账金额 住房账户 医疗账户 养老个人 养老补充".split(" ")
        pt = PrettyTable(print_head)
        for line in self.__records:
            pt.add_row((line['belongMonth'], line['renderType'], line['baseMoney'], line['sumMoney'],
                        line['medicalHosingAcc'], line['retiredMedicalAcc'], line['commonRetiredAcc'],
                        line['specilRetiredAcc']))
        return pt

    def months(self):
        """ 计算累积的月份 """
        return len(self.__records)

    def last_month(self):
        """ 计算最后一次社保缴费的月份 """
        return self.__records[-1]['belongMonth']

    def mail(self):
        """ 将社保记录转为邮件的格式 """
        pt = self.pretty()

        title = '社保查询%s记录,累积缴纳%s个月,最近一次缴纳月份为%s ……' % \
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.months(), self.last_month())
        content = '<div>%s<div>%s' % (title, pt.get_html_string())

        return {'title': title, 'content': content}

