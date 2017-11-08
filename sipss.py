#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2017/11/4 下午2:49
# @Author  : fanqiang
# @Site    : 
# @File    : sipss.py
# @Software: PyCharm

"""查询苏州园区社保缴费记录

Usage:
    sipss
    sipss  <username> <password>  [--m=<mail>]

Options:
    -h,--help       显示帮助菜单
    --m=<mail>      发送到邮箱,不设置此选项打印到控制台


Example:
    sipss
    sipss  uname passowrd  --m=username@gamil.com
"""

import configuration
from social_security.spider import SipSocialSecuritySpider
from utils import mail

from docopt import docopt


def conf():
    """从配置文件中读取"""
    return configuration.get('sipss', 'user'), configuration.get('sipss', 'password'), configuration.get('sipss',
                                                                                                         'recipients')


def cli():
    """通过命令行读取"""
    arguments = docopt(__doc__)
    return arguments['<username>'], arguments['<password>'], arguments['--m']


if __name__ == '__main__':
    user, password, recipients = cli()
    if not user or not password:
        user, password, recipients = conf()

    ss = SipSocialSecuritySpider(user, password)
    ss.login()
    records = ss.fetch_records()

    if not recipients:
        print(records.pretty().get_string())
    else:
        mail_dict = records.mail()
        mail.send_email(recipients, mail_dict['title'], mail_dict['content'])
