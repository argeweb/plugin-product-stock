#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, Fields, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search


class Stock(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search)
        pagination_limit = 10

    class Scaffold:
        display_properties_in_list = ("name", "title", "is_enable", "category")

    @route_menu(list_name=u"backend", text=u"庫存", sort=1201, group=u"庫存管理")
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u"backend", text=u"出庫", sort=1203, group=u"庫存管理", need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u"backend", text=u"入庫", sort=1204, group=u"庫存管理")
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u"backend", text=u"盤點", sort=1205, group=u"庫存管理")
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u"backend", text=u"報表", sort=1207, group=u"庫存管理", need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u"backend", text=u"供應商設置", sort=1210, group=u"庫存管理", need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u"backend", text=u"出入庫性質設置", sort=1211, group=u"庫存管理")
    def admin_list(self):
        return scaffold.list(self)
