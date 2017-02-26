#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from google.appengine.ext import ndb
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
        for loop_index in xrange(1, len(list_need_to_append)):
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
            for loop_index in xrange(1, loop_item_len + 1):
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
        pagination_limit = 10

    class Scaffold:
        display_in_list = ('sku_full_name', 'product', 'title', 'quantity', 'is_enable', 'can_be_purchased')
        disabled_in_form = ('product', 'last_in_quantity', 'last_in_datetime', 'last_out_quantity', 'last_out_datetime')

    @route_menu(list_name=u'backend', text=u'出庫', sort=1203, group=u'產品維護', need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'入庫', sort=1204, group=u'產品維護')
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'盤點', sort=1205, group=u'產品維護')
    def admin_list(self):
        return scaffold.list(self)

    @route
    def admin_stock_in(self):
        from ..models.stock_history_model import create_history
        from ..models.stock_history_detail_model import create_history_detail
        self.meta.change_view('json')
        data = []
        length = self.params.get_integer('length')
        remake = self.params.get_string('remake')
        w = self.params.get_ndb_record('warehouse')
        history = create_history(self.application_user, u'產品入庫', remake)
        for index in xrange(0, length):
            r = self.params.get_ndb_record('sku-key-%s' % str(index))
            if r is not None:
                quantity = self.params.get_integer('sku-quantity-%s' % str(index))
                if quantity != 0:
                    create_history_detail(history, r, u'入庫', quantity, w)
                    r.quantity = r.quantity + quantity
                    r.last_in_quantity = r.quantity
                    r.last_in_datetime = datetime.now()
                    data.append(SKUIW_Model.in_warehouse(r, w, quantity))
                    r.put()
        self.context['message'] = u'完成'
        self.context['data'] = data

    @route
    def admin_stock_out(self):
        from ..models.stock_history_model import create_history
        self.meta.change_view('json')
        length = self.params.get_integer('length')
        remake = self.params.get_string('remake')
        w = self.params.get_ndb_record('warehouse')
        check_list = []
        msg = []
        data = []
        for index in xrange(0, length):
            r = self.params.get_ndb_record('sku-key-%s' % str(index))
            if r is not None:
                quantity = self.params.get_integer('sku-quantity-%s' % str(index))
                if quantity > 0:
                    sku_record = SKUIW_Model.get_or_create(r, w)
                    c = sku_record.quantity - quantity
                    if c < 0:
                        msg.append(u'錯誤 [ %s ] 的數量不足 %s 個，缺少 %s 個' % (r.title, str(quantity), str(-c)))
                    check_list.append({
                        'sku': r,
                        'sku_in_warehouse': sku_record,
                        'quantity': quantity,
                        'check': c,
                        'msg': msg
                    })
                    data.append(sku_record)
        if len(msg) > 0:
            create_history(self.application_user, u'產品出庫', remake, False, u'<br>\n'.join(msg))
            self.context['message'] = u'<br>\n'.join(msg)
            self.context['data'] = data
            return
        data = []
        history = create_history(self.application_user, u'產品出庫', remake)
        for item in check_list:
            sku = item['sku']
            sku_in_warehouse = item['sku_in_warehouse']
            quantity = item['quantity']
            sku_in_warehouse.quantity = sku_in_warehouse.quantity - quantity
            sku_in_warehouse.put()
            sku.quantity = sku.quantity - quantity
            sku.last_out_quantity = sku.quantity
            sku.last_out_datetime = datetime.now()
            sku.put()
            data.append(sku_in_warehouse)
        self.context['message'] = u'完成'
        self.context['data'] = data

    @route
    def admin_list_for_side_panel(self, target=''):
        self.context['warehouse'] = WarehouseModel.all()
        if target == '--no-record--':
            self.context['no_record_data'] = True
            return
        product_record = self.util.decode_key(target).get()
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
            return model.query(model.product == product_record.key).order(model.sort)

        self.scaffold.query_factory = query_factory
        scaffold.list(self)
        spec_records = self.context[self.scaffold.singular].fetch()

        need_to_insert_spec_items = get_need_update_spec_item_list(spec_lists, spec_records)

        if do_update:
            spec_records = []
            for update_item in need_to_insert_spec_items:
                m = self.meta.Model()
                m.spec_full_name = update_item
                m.product = product_record.key
                m.put()
                spec_records.append(m)
        else:
            if len(need_to_insert_spec_items) > 0:
                self.context['need_update'] = True
                self.context['need_to_insert_spec_items'] = need_to_insert_spec_items
        self.context['len_records'] = len(spec_records)
        self.context['spec_records'] = spec_records

    @route
    def get_sku_detail(self):
        self.meta.change_view('json')
        product = self.params.get_ndb_record('product')
        if product is None or product.is_enable is False:
            return self.json([])

        model = self.meta.Model
        query = model.query(model.product == product.key).order(model.sort)
        return self.json(query.fetch())

    @route
    def admin_get_sku_detail(self):
        self.meta.change_view('json')
        product = self.params.get_ndb_record('product')

        def query_factory(controller):
            model = controller.meta.Model
            return model.query(model.product == product.key).order(model.sort)

        self.scaffold.query_factory = query_factory
        return scaffold.list(self)

    @route
    def admin_get_warehouse_detail(self):
        self.meta.change_view('json')
        product = self.params.get_ndb_record('product')
        warehouse = self.params.get_ndb_record('warehouse')
        if product is None or warehouse is None:
            self.context['data'] = None
            return
        data = SKUIW_Model.get_all_with_product(product, warehouse).fetch()
        if len(data) <= 0:
            data = SKUIW_Model.create_sku_by_product(product, warehouse)
        self.context['data'] = data

    @route
    def admin_insert_spec_to_product_records(self, target=''):
        pass
