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
from ..models.warehouse_model import WarehouseModel


class StockHistory(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search)
        pagination_limit = 10

    class Scaffold:
        display_in_list = ('sku_full_name', 'category', 'title', 'quantity', 'is_enable', 'can_be_purchased')
        disabled_in_form = ('category', 'last_in_quantity', 'last_in_datetime', 'last_out_quantity', 'last_out_datetime')

    @route_menu(list_name=u'backend', text=u'庫存', sort=1201, group=u'庫存管理')
    def admin_list(self):
        return scaffold.list(self)