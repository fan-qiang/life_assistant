#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2017/11/4 下午2:49
# @Author  : fanqiang
# @Site    : 
# @File    : sipsi.py
# @Software: PyCharm

"""查询苏州园区社保缴费记录

Usage:
    sipsi
    sipsi  <username> <password>  [--m=<mail>]

Options:
    -h,--help       显示帮助菜单
    --m=<mail>      发送到邮箱,不设置此选项打印到控
Example:
    sipsi
    sipsi uname passowrd  --m=username@gamil.com
"""

import configuration
from social_insurance.spider import SipSocialInsuranceSpider
from utils import mail

from docopt import docopt


def conf():
    """从配置文件中读取"""
    return configuration.get('sipsi', 'user'), configuration.get('sipsi', 'password'), configuration.get('sipsi',
                                                                                                         'recipients')


def cli():
    """通过命令行读取"""
    arguments = docopt(__doc__)
    return arguments['<username>'], arguments['<password>'], arguments['--m']


if __name__ == '__main__':
    user, password, recipients = cli()
    if not user or not password:
        user, password, recipients = conf()

    ss = SipSocialInsuranceSpider(user, password)
    ss.login()
    records = ss.fetch_records()

    if not recipients:
        print(records.pretty().get_string())
    else:
        mail_dict = records.mail()
        mail.send_email(recipients, mail_dict['title'], mail_dict['content'])
