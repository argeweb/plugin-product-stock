#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/4/22.
from google.appengine.ext import ndb
from datetime import datetime
from argeweb import Controller, scaffold, route_menu, Fields, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search
from ..models.warehouse_model import WarehouseModel


class StockTemporaryItem(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search)

    class Scaffold:
        display_in_list = ('sku_full_name', 'product', 'title', 'quantity', 'is_enable', 'can_be_purchased')
        disabled_in_form = ('product', 'last_in_quantity', 'last_in_datetime', 'last_out_quantity', 'last_out_datetime')

    @route_menu(list_name=u'backend', text=u'出庫', sort=1203, group=u'產品維護', need_hr=True, parameter=u'operation=out_stock')
    @route_menu(list_name=u'backend', text=u'入庫', sort=1204, group=u'產品維護', parameter=u'operation=in_stock')
    @route_menu(list_name=u'backend', text=u'盤點', sort=1205, group=u'產品維護', parameter=u'operation=check')
    def admin_list(self):
        if 'query' not in self.request.params:
            def query_factory_with_operation(controller):
                return controller.meta.Model.all_with_request_type(controller.status)

            setattr(self, 'operation', self.params.get_string('operation', ''))
            self.scaffold.query_factory = query_factory_with_operation
        return scaffold.list(self)

