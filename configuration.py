#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2017/11/4 下午1:35
# @Author  : fanqiang
# @Site    : 
# @File    : configuration.py
# @Software: PyCharm
import configparser
import pathlib

_config = configparser.ConfigParser()
path = pathlib.Path(__file__)
_config.read(str(path.absolute().parent) + "/config.cfg", encoding='utf-8')


def get(section, key):
    return _config.get(section, key)
