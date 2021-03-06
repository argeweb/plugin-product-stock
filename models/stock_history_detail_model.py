#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from stock_history_model import StockHistoryModel


class StockHistoryDetailModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
        }

    history = Fields.KeyProperty(verbose_name=u'歷史記錄', kind=StockHistoryModel)
    product_name = Fields.StringProperty(verbose_name=u'產品名稱')
    product_image = Fields.StringProperty(verbose_name=u'產品圖片')
    sku_object = Fields.KeyProperty(verbose_name=u'SKU 對象')
    spec_full_name = Fields.SearchingHelperProperty(verbose_name=u'完整規格名稱', target='sku_object', target_field_name='spec_full_name')
    sku_full_name = Fields.SearchingHelperProperty(verbose_name=u'sku 編號', target='sku_object', target_field_name='sku_full_name')
    operation_type = Fields.StringProperty(verbose_name=u'操作類型')  # 出庫、入庫、轉倉
    warehouse = Fields.StringProperty(verbose_name=u'倉庫')
    warehouse_target = Fields.StringProperty(verbose_name=u'目標倉庫')
    quantity = Fields.IntegerProperty(verbose_name=u'數量')

    @classmethod
    def all_with_history(cls, history):
        return cls.query(cls.history == history.key).order(-cls.sort)

    @property
    def sku_instance(self):
        if not hasattr(self, '_sku'):
            self._sku = self.sku_object.get()
        return self._sku

def create_history_detail(history, sku, operation_type, quantity, warehouse, warehouse_target=None):
    product = sku.product_object.get()
    r = StockHistoryDetailModel()
    r.history = history.key
    r.product_name = product.title
    r.product_image = product.image
    r.sku_object = sku.key
    r.operation_type = operation_type
    r.quantity = quantity
    r.warehouse = warehouse.title
    if warehouse_target is None:
        r.warehouse_target = u'無'
    else:
        r.warehouse_target = warehouse_target.title
    r.put()
    return r
