#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, Fields, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search
from ..models.warehouse_model import WarehouseModel


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
        components = (scaffold.Scaffolding, Pagination, Search)
        pagination_limit = 10

    class Scaffold:
        display_in_list = ('sku_full_name', 'category', 'title', 'quantity', 'is_enable', 'can_be_purchased')

    @route_menu(list_name=u'backend', text=u'庫存', sort=1201, group=u'庫存管理')
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'出庫', sort=1203, group=u'庫存管理', need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'入庫', sort=1204, group=u'庫存管理')
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'盤點', sort=1205, group=u'庫存管理')
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'報表', sort=1207, group=u'庫存管理', need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'供應商設置', sort=1210, group=u'庫存管理', need_hr=True)
    def admin_list(self):
        return scaffold.list(self)

    @route_menu(list_name=u'backend', text=u'出入庫性質設置', sort=1211, group=u'庫存管理')
    def admin_list(self):
        return scaffold.list(self)

    @route
    def admin_list_for_side_panel(self, target=''):
        self.context['ware_house'] = WarehouseModel.all()
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
            return model.query(model.category == product_record.key).order(model.sort)

        self.scaffold.query_factory = query_factory
        scaffold.list(self)
        spec_records = self.context[self.scaffold.singular].fetch()

        need_to_insert_spec_items = get_need_update_spec_item_list(spec_lists, spec_records)

        if do_update:
            for update_item in need_to_insert_spec_items:
                m = self.meta.Model()
                m.spec_full_name = update_item
                m.category = product_record.key
                m.put()
            spec_records = self.context[self.scaffold.singular].fetch()
        else:
            if len(need_to_insert_spec_items) > 0:
                self.context['need_update'] = True
                self.context['need_to_insert_spec_items'] = need_to_insert_spec_items
        self.context['len_records'] = len(spec_records)
        self.context['spec_records'] = spec_records

    @route
    def admin_insert_spec_to_product_records(self, target=''):
        pass
