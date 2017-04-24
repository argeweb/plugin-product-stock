#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product.models.product_model import ProductModel, ProductCategoryModel
from stock_keeping_unit_model import StockKeepingUnitModel
from warehouse_model import WarehouseModel
from datetime import datetime


class StockKeepingUnitInWarehouseModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
            'sku_full_name': u'sku 編號'
        }

    sku = Fields.KeyProperty(kind=StockKeepingUnitModel, verbose_name=u'所屬 SKU')
    warehouse = Fields.KeyProperty(kind=WarehouseModel, verbose_name=u'所屬倉庫')
    product = Fields.KeyProperty(kind=ProductModel, verbose_name=u'所屬產品')
    quantity = Fields.IntegerProperty(verbose_name=u'在庫數量', default=0)

    @classmethod
    def stock_in(cls, warehouse, sku, quantity):
        record = cls.get_or_create(sku=sku,warehouse=warehouse)
        record.quantity = int(record.quantity) + int(quantity)
        record.put()

        sku.quantity = sku.quantity + quantity
        sku.last_in_quantity = sku.quantity
        sku.last_in_datetime = datetime.now()
        sku.put()
        return record

    @classmethod
    def stock_out_check(cls, warehouse, sku, quantity, auto_fill=False):
        record = cls.get_or_create(sku=sku,warehouse=warehouse)
        c = record.quantity - quantity
        if c < 0 and auto_fill is False:
            raise ValueError(u'錯誤 [ %s ] 的數量不足 %s 個，缺少 %s 個' % (sku.spec_full_name, str(quantity), str(-c)))

    @classmethod
    def stock_out(cls, warehouse, sku, quantity, auto_fill=False):
        record = cls.get_or_create(sku=sku,warehouse=warehouse)
        record.quantity = record.quantity - quantity
        record.put()

        sku.quantity = sku.quantity - quantity
        sku.last_out_quantity = sku.quantity
        sku.last_out_datetime = datetime.now()
        sku.put()
        return record

    @classmethod
    def get_or_create(cls, sku, warehouse, quantity=0):
        record = cls.query(cls.sku==sku.key, cls.warehouse==warehouse.key).get()
        if record is None:
            record = cls()
            record.sku = sku.key
            record.product = sku.product_object
            record.warehouse = warehouse.key
            record.quantity = quantity
        record.put()
        return record

    @classmethod
    def get_all_with_product(cls,product, warehouse=None):
        if warehouse is None:
            return cls.query(cls.product==product.key)
        else:
            return cls.query(cls.product==product.key, cls.warehouse==warehouse.key)

    @classmethod
    def create_sku_by_product(cls, product, warehouse=None):
        from stock_keeping_unit_model import StockKeepingUnitModel as SKU
        sku_list = SKU.query(SKU.product_object == product.key).fetch()
        sku_list_in_warehouse = []
        for item in sku_list:
            sku_list_in_warehouse.append(cls.get_or_create(item, warehouse))
        return sku_list_in_warehouse
