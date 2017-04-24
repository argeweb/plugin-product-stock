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

    @route_menu(list_name=u'backend', text=u'庫存記錄', sort=1207, group=u'產品維護')
    def admin_list(self):
        return scaffold.list(self)

    @route
    def admin_create_with_order(self, order_key):
        import time
        from plugins.order.models.order_item_model import OrderItemModel
        from ..models.stock_temporary_item_model import StockTemporaryItemModel
        request_type = self.params.get_string('request_type')
        operation = u'訂單全部出庫'
        if request_type == 'stock_only':
            operation = u'訂單庫存出庫'
        if request_type == 'pre_order_only':
            operation = u'訂單預購出庫'

        order = self.params.get_ndb_record(order_key)
        temporary_key = self.util.encode_key(order) + '-' + str(time.time())
        for item in OrderItemModel.all_with_order(order):
            if request_type == 'all' \
                    or ((item.order_type_value == 0) and (request_type == 'stock_only')) \
                    or ((item.order_type_value == 1) and (request_type == 'pre_order_only')):
                StockTemporaryItemModel.create_from_order_item(item, temporary_key)

        def scaffold_after_save(**kwargs):
            item = kwargs['item']

        self.events.scaffold_after_save += scaffold_after_save
        self.context['temporary_key'] = temporary_key
        return scaffold.add(self, user=self.application_user.key, user_name=self.application_user.name,
                            temporary_key=temporary_key, operation=operation, order=order.key, temporary_items=temporary_key)
