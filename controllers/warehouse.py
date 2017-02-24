#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, Fields, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search


class Warehouse(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search)
        pagination_limit = 10

    class Scaffold:
        display_in_list = ('name', 'title', 'address', 'telephone')

    @route_menu(list_name=u'backend', text=u'倉庫設置', sort=9932, group=u'系統設定')
    def admin_list(self):
        return scaffold.list(self)