#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2017/11/4 下午1:43
# @Author  : fanqiang
# @Site    : 
# @File    : mail.py
# @Software: PyCharm

"""
    邮件发送的工具类
"""

import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import configuration


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email(to, subject, html_content):
    """
        根据传入的数据发送邮件
        Args:
            to: 邮件接收人地址
            subject: 邮件主题
            html_content: 邮件内容
    """
    user = configuration.get("mail", "user")
    password = configuration.get("mail", "password")
    smtp_server = configuration.get("mail", "server")

    from_name = configuration.get("mail", "from")

    msg = MIMEMultipart()
    msg['From'] = _format_addr('%s <%s>' % (from_name, user))
    msg['To'] = _format_addr(to)
    msg['Subject'] = Header(subject).encode()

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    port = configuration.get("mail", "port")

    server = smtplib.SMTP(smtp_server)  # SMTP 协议默认端口是25
    server.starttls()
    server.login(user, password)
    server.sendmail(user, to, msg.as_string())
    server.quit()
