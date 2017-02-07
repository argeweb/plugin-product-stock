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

class StockKeepingUnitInWarehouseModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
            'sku_full_name': u'sku 編號'
        }

    sku = Fields.CategoryProperty(kind=StockKeepingUnitModel, verbose_name=u'所屬 SKU')
    warehouse = Fields.CategoryProperty(kind=WarehouseModel, verbose_name=u'所屬倉庫')
    product = Fields.CategoryProperty(kind=ProductModel, verbose_name=u'所屬產品')
    quantity = Fields.IntegerProperty(verbose_name=u'在庫數量', default=0)

    @classmethod
    def in_warehouse(cls, sku, warehouse, quantity):
        record = cls.query(cls.sku==sku.key,cls.warehouse==warehouse.key).get()
        if record is None:
            record = cls()
            record.sku = sku.key
            record.product = sku.category
            record.warehouse = warehouse.key
            record.quantity = 0
        record.quantity = int(record.quantity) + int(quantity)
        record.put()
        return record.quantity

    @classmethod
    def out_warehouse(cls, sku, warehouse, quantity):
        record = cls.query(cls.sku==sku.key,cls.warehouse==warehouse.key).get()
        if record is None:
            record = cls()
            record.sku = sku.key
            record.product = sku.category
            record.warehouse = warehouse.key
            record.quantity = 0
        record.quantity = int(record.quantity) - int(quantity)
        if record.quantity <= 0:
            return -1
        record.put()
        return record.quantity

    @classmethod
    def get_all_with_product(cls,product, warehouse=None, quantity=0):
        if warehouse is None:
            return cls.query(cls.product==product.key, cls.quantity>0)
        else:
            return cls.query(cls.product==product.key, cls.warehouse==warehouse.key, cls.quantity>quantity)

