#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2017/11/4 下午1:35
# @Author  : fanqiang
# @Site    : 
# @File    : configuration.py
# @Software: PyCharm
import configparser
import pathlib

__config = configparser.ConfigParser()
path = pathlib.Path(__file__)
__config.read(str(path.absolute().parent) + "/config.ini")


def get(section, key):
    return __config.get(section, key)
