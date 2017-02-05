#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields


class WarehouseModel(BasicModel):
    name = Fields.HiddenProperty(verbose_name=u'系統編號')
    title = Fields.StringProperty(verbose_name=u'倉庫名稱')
    address = Fields.StringProperty(verbose_name=u'地址')
    telephone = Fields.StringProperty(verbose_name=u'電話')

