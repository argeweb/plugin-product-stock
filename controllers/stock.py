#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from datetime import datetime
from argeweb import Controller, scaffold, route_menu, Fields, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search
from ..models.warehouse_model import WarehouseModel
from ..models.stock_history_model import StockHistoryModel
from ..models.stock_keeping_unit_model import StockKeepingUnitModel
from ..models.stock_keeping_unit_in_warehouse_model import StockKeepingUnitInWarehouseModel as SKUIW_Model

def process_spec(spec_data):
    """ 格式化產品規格資料、去除空白
    :param spec_data: '尺寸:S, L'
    :return:
        ['尺寸', 'S', 'L']
    """
    if spec_data is u'' or spec_data is None:
        return []
    spec_split = spec_data.split(u':')
    if len(spec_split) <= 1:
        return []
    return_data = [x.strip() for x in spec_split[1].split(',')]
    return_data.insert(0, spec_split[0].strip())
    return return_data


def gen_spec_item(list_exist, list_need_to_append):
    """ 將 list_need_to_append 陣列合併至，list_exist 成一維的陣列
    :param list_exist: ['尺寸:s,大小:5', '尺寸:s,大小:6']
    :param list_need_to_append: ['顏色', '紅', '綠']
    :return:
        ['尺寸:s,大小:5,顏色:紅', '尺寸:s,大小:6,顏色:紅', '尺寸:s,大小:5,顏色:綠', '尺寸:s,大小:6,顏色:綠']
    """
    return_list_exist = []
    for exist_item in list_exist:
        for loop_index in range(1, len(list_need_to_append)):
            new_item = exist_item + u',' + list_need_to_append[0] + u':' + list_need_to_append[loop_index]
            if new_item not in return_list_exist:
                return_list_exist.append(new_item)
    return return_list_exist


def get_spec_lists(original_specs):
    """ 合併各規格陣列，成一維的陣列
    :param original_specs: an array like [['尺寸', 's', 'm', 'l'], ['大小', '5', '6']]
    :return:
        ['尺寸:s,大小:5','尺寸:m,大小:5','尺寸:l,大小:5','尺寸:s,大小:6','尺寸:m,大小:6','尺寸:l,大小:6']
    """
    total = 0
    spec_lists = []
    for loop_item_spec_list in original_specs:
        loop_item_len = len(loop_item_spec_list) - 1
        if total == 0 and loop_item_len > 0:
            for loop_index in range(1, loop_item_len + 1):
                if loop_item_spec_list[loop_index] != u'':
                    total += 1
                    new_item = loop_item_spec_list[0] + u':' + loop_item_spec_list[loop_index]
                    spec_lists.append(new_item)
        elif loop_item_len > 0:
            total *= loop_item_len
            spec_lists = gen_spec_item(spec_lists, loop_item_spec_list)
    return total, spec_lists


def get_need_update_spec_item_list(new_spec_list, old_spec_records):
    """ 比較應有的規格與現有規格，然後回傳需要新增的規格資料
    :param new_spec_list: ['尺寸:s,大小:5','尺寸:m,大小:5']
    :param old_spec_records: ndb records
    :return:
        ['尺寸:m,大小:5']
    """
    need_to_insert_spec_items = []
    if old_spec_records is not None:
        for spec_item in new_spec_list:
            is_find = False
            for spec_record in old_spec_records:
                if spec_record.spec_full_name == spec_item:
                    is_find = True
            if is_find is False:
                need_to_insert_spec_items.append(spec_item)
    return need_to_insert_spec_items


class Stock(Controller):
    class Meta:
        Model = StockKeepingUnitModel
        components = (scaffold.Scaffolding, Pagination, Search)

    class Scaffold:
        display_in_list = ('sku_full_name', 'product', 'title', 'quantity', 'is_enable', 'can_be_purchased')
        disabled_in_form = ('product_no', 'product', 'last_in_quantity', 'last_in_datetime', 'last_out_quantity', 'last_out_datetime')
        hidden_in_form = ('product_object')

    @route
    def taskqueue_reset_order_quantity(self):
        order = self.params.get_ndb_record('order')
        history = self.params.get_ndb_record('history')
        history_sku_list = []
        order_item_sku_list = []
        for detail in history.details:
            history_sku_list.append({
                'history_detail': detail,
                'sku': detail.sku_instance
            })
        for item in order.items:
            order_item_sku_list.append({
                'order_item': item,
                'sku': item.sku_instance
            })
        for o in order_item_sku_list:
            o_item = o['order_item']
            o_sku = o['sku']
            for h in history_sku_list:
                h_item = h['history_detail']
                h_sku = h['sku']
                if h_sku == o_sku:
                    if o_item.quantity_has_count > 0 and h_item.quantity > 0:
                        if o_item.order_type_value == 0:
                            o_sku.change_in_order_quantity(o_item.quantity_has_count)
                        if o_item.order_type_value == 1:
                            o_sku.change_pre_order_quantity(h_item.quantity)
                        o_sku.put()
                        o_item.quantity_has_count = o_item.quantity_has_count - h_item.quantity
                        if o_item.quantity_has_count < 0:
                            o_item.quantity_has_count = 0
                        o_item.put()
                        continue
        return 'task'

    @route_menu(list_name=u'backend', text=u'最小庫存單位', sort=1206, group=u'產品銷售', need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route
    def admin_stock_process(self):
        from ..models.stock_history_model import create_history
        self.meta.change_view('json')
        msg = []
        data = []
        check_list = []
        length = self.params.get_integer('length')
        remake = self.params.get_string('remake')
        warehouse = self.params.get_ndb_record('warehouse')
        operation = self.params.get_string('operation', '庫存管理')
        auto_fill = self.params.get_boolean('auto_fill', False)
        target_warehouse = self.params.get_ndb_record('target_warehouse')

        for index in range(0, length):
            sku = self.params.get_ndb_record('sku_key_%s' % index)
            quantity = self.params.get_integer('sku_quantity_%s' % index)
            operation_type = self.params.get_string('sku_operation_type_%s' % index)
            if sku is not None and quantity != 0:
                if operation_type == 'in':
                    check_list.append({
                        'sku': sku,
                        'quantity': quantity,
                        'operation_type': operation_type
                    })
                if operation_type == 'out':
                    try:
                        warehouse.stock_out_check(sku, quantity, auto_fill=auto_fill)
                        check_list.append({
                            'sku': sku,
                            'quantity': quantity,
                            'operation_type': operation_type
                        })
                    except Exception as error:
                        msg.append(u'%s' % error)
                if operation_type == 'move':
                    target_warehouse = self.params.get_ndb_record('target_warehouse')
                    try:
                        pass
                    except Exception as error:
                        msg.append(u'%s' % error)
                    # 轉倉

        if len(msg) > 0:
            create_history(self.application_user, operation, remake, False, u'<br>\n'.join(msg))
            self.context['message'] = u'<br>\n'.join(msg)
            self.context['data'] = {'items': data}
            return

        order = self.params.get_ndb_record('order_key')
        history = create_history(self.application_user, operation, remake, order=order)
        if order is not None:
            order.need_reset_stock_quantity = True
            order.put()
            task = taskqueue.add(
                url=self.uri('taskqueue:product_stock:stock:reset_order_quantity'),
                params={'order': self.util.encode_key(order), 'history': self.util.encode_key(history)})

        for item in check_list:
            sku = item['sku']
            quantity = item['quantity']
            operation_type = item['operation_type']
            if operation_type == 'in':
                data.append(warehouse.stock_in(sku, quantity, history, u'入庫'))
            if operation_type == 'out':
                data.append(warehouse.stock_out(sku, quantity, history, u'出庫', auto_fill))
        self.context['message'] = u'完成'
        self.context['data'] = {'items': data}

    def get_sku_instance_list(self, order_items, request_type):
        sku_instance_list = []
        _order_items = []
        for item in order_items:
            if request_type == 'all' \
                    or ((item.order_type_value == 0) and (request_type == 'stock_only')) \
                    or ((item.order_type_value == 1) and (request_type == 'pre_order_only')):
                _order_items.append(item)

        for item in _order_items:
            sku_name = self.util.encode_key(item.sku)
            sku_target = None
            for sku_item in sku_instance_list:
                if sku_item['name'] == sku_name:
                    sku_target = sku_item

            if sku_target is None:
                sku_target = {
                    'name': sku_name,
                    'sku_key': self.util.encode_key(item.sku_instance),
                    'sku_product_name': item.sku_instance.product,
                    'sku_spec_full_name': item.sku_instance.spec_full_name,
                    'need_stock_out_quantity': item.quantity,
                    'need_stock_in_quantity': 0
                }
                sku_instance_list.append(sku_target)
            else:
                sku_target['need_stock_out_quantity'] += item.quantity
        return sku_instance_list

    @route
    def admin_side_panel_for_order(self, order_key=''):
        order = self.params.get_ndb_record(order_key)
        request_type = self.params.get_string('request_type')
        self.context['sku_instance_list'] = self.get_sku_instance_list(order.items, request_type)
        self.context['warehouse'] = WarehouseModel.all()
        self.context['order'] = order
        self.context['operation'] = u'全部出庫'
        if request_type == 'stock_only':
            self.context['operation'] = u'庫存出庫'
        if request_type == 'pre_order_only':
            self.context['operation'] = u'預購出庫'
        return scaffold.list(self)

    @route
    def admin_side_panel_for_product(self, target=''):
        self.context['warehouse'] = WarehouseModel.all()
        if target == '--no-record--':
            self.context['no_record_data'] = True
            return
        product_record = self.params.get_ndb_record(target)
        self.context['product'] = product_record

        total, spec_lists = get_spec_lists([process_spec(product_record.spec_1), process_spec(product_record.spec_2),
                                            process_spec(product_record.spec_3), process_spec(product_record.spec_4),
                                            process_spec(product_record.spec_5)])

        self.context['spec'] = spec_lists
        self.context['total'] = total
        if total == 0:
            self.context['no_spec_data'] = True
            return

        do_update = self.params.get_boolean('update', False)
        if do_update is False:
            self.context['update_url'] = self.request.path + "?update=True"

        self.context['has_record'] = True

        def query_factory(controller):
            model = controller.meta.Model
            return model.query(model.product_object == product_record.key).order(model.sort)
        self.scaffold.query_factory = query_factory
        scaffold.list(self)

        spec_records = self.context[self.scaffold.singular].fetch()
        need_to_insert_spec_items = get_need_update_spec_item_list(spec_lists, spec_records)

        if do_update:
            spec_records = []
            for update_item in need_to_insert_spec_items:
                m = self.meta.Model()
                m.spec_full_name = update_item
                m.product_object = product_record.key
                m.put()
                spec_records.append(m)
        else:
            if len(need_to_insert_spec_items) > 0:
                self.context['need_update'] = True
                self.context['need_to_insert_spec_items'] = need_to_insert_spec_items
        self.context['len_records'] = len(spec_records)
        self.context['spec_records'] = spec_records

    @route
    def admin_get_sku_detail(self):
        def query_factory(controller):
            product = controller.params.get_ndb_record('product')
            model = controller.meta.Model
            return model.query(model.product_object == product.key).order(model.sort)

        self.scaffold.query_factory = query_factory
        return scaffold.list(self, True)

    @route
    def admin_get_sku_detail_with_order(self):
        def query_factory(controller):
            from plugins.order.models.order_item_model import OrderItemModel
            warehouse = controller.params.get_ndb_record('warehouse')
            order = controller.params.get_ndb_record('order')
            order_items = OrderItemModel.all_with_order(order)
            data = []
            for item in order_items:
                data.append(item.sku.get())
            return data

        self.scaffold.query_factory = query_factory
        return scaffold.list(self, True)

    @route
    def admin_get_warehouse_detail(self):
        # TODO 改用 scaffold
        self.meta.change_view('json')
        product = self.params.get_ndb_record('product')
        warehouse = self.params.get_ndb_record('warehouse')
        if product is None or warehouse is None:
            self.context['data'] = None
            return
        data = SKUIW_Model.get_all_with_product(product, warehouse).fetch()
        if len(data) <= 0:
            data = SKUIW_Model.create_sku_by_product(product, warehouse)
        self.context['data'] = {'items': data}

    @route
    def admin_get_warehouse_detail_with_sku(self):
        self.meta.change_view('json')
        items = self.params.get_string('sku_items').split(',')
        warehouse = self.params.get_ndb_record('warehouse')
        warehouse_sku_items = []
        for item in items:
            sku = self.params.get_ndb_record(item)
            if sku is not None:
                warehouse_sku = SKUIW_Model.get_or_create(sku, warehouse)
                warehouse_sku_items.append(warehouse_sku)
        self.context['data'] = {'items': warehouse_sku_items}

    @route
    def admin_get_warehouse_detail_with_order(self):
        # TODO 改用 scaffold
        self.meta.change_view('json')
        from plugins.order.models.order_item_model import OrderItemModel
        warehouse = self.params.get_ndb_record('warehouse')
        order = self.params.get_ndb_record('order')
        order_items = OrderItemModel.all_with_order(order)
        data = []
        for item in order_items:
            sku = item.sku.get()
            data.append(SKUIW_Model.get_or_create(sku=sku, warehouse=warehouse))

        if order is None or warehouse is None:
            self.context['data'] = None
            return
        self.context['data'] = {'items': data}

    @route
    def taskqueue_update_sku_information(self):
        self.meta.change_view('json')
        product = self.params.get_ndb_record('product')
        sku_items = StockKeepingUnitModel.all_enable(product=product)
        for item in sku_items:
            item.put()
        self.context['data'] = {'update': sku_items}