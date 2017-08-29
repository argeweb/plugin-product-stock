#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu


class Warehouse(Controller):
    class Scaffold:
        display_in_list = ['name', 'title', 'address', 'telephone']

    @route_menu(list_name=u'backend', group=u'產品管理', text=u'倉庫設置', sort=1355)
    def admin_list(self):
        return scaffold.list(self)