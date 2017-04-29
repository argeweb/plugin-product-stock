#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from datetime import datetime
from argeweb import Controller, scaffold, route_menu, Fields, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search


class StockHistory(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search)

    class Scaffold:
        # display_in_list = ('sku_full_name', 'category', 'title', 'quantity', 'is_enable', 'can_be_purchased')
        disabled_in_form = ('user', 'user_name', 'operation')
        hidden_in_form = ('temporary_key', 'status', 'result')

    @route_menu(list_name=u'backend', text=u'庫存記錄', sort=1207, group=u'產品銷售')
    def admin_list(self):
        return scaffold.list(self)
