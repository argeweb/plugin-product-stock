#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product_stock.models.stock_keeping_unit_model import StockKeepingUnitModel
from plugins.application_user.models.application_user_model import ApplicationUserModel
from plugins.product.models.product_config_model import ProductConfigModel
from time import time


class StockTemporaryItemModel(BasicModel):
    name = Fields.StringProperty(verbose_name=u'識別名稱')
    sku = Fields.KeyProperty(verbose_name=u'最小庫存單位', kind=StockKeepingUnitModel)
    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)
    temporary = Fields.StringProperty(verbose_name=u'暫存的對象')
    need_stock_out_quantity = Fields.IntegerProperty(verbose_name=u'需出庫的數量', default=0)
    need_stock_in_quantity = Fields.IntegerProperty(verbose_name=u'需入庫的數量', default=0)

    title = Fields.StringProperty(verbose_name=u'產品名稱')
    product_no = Fields.StringProperty(verbose_name=u'產品編號')
    product_name = Fields.StringProperty(verbose_name=u'產品圖片', default=u'')
    product_image = Fields.StringProperty(verbose_name=u'產品圖片', default=u'')
    sku_full_name = Fields.StringProperty(verbose_name=u'產品最小庫存名稱')
    spec_full_name = Fields.StringProperty(verbose_name=u'完整規格名稱')
    price = Fields.FloatProperty(verbose_name=u'銷售價格', default=-1)
    cost = Fields.FloatProperty(verbose_name=u'成本', default=0.0)
    quantity = Fields.IntegerProperty(verbose_name=u'數量', default=0)
    quantity_has_count = Fields.IntegerProperty(verbose_name=u'已計入庫存的數量', default=0)
    can_add_to_order = Fields.BooleanProperty(verbose_name=u'加至訂單中', default=False)
    expired_time = Fields.FloatProperty(verbose_name=u'庫存回收時間')

    #  0 = 現貨, 1=預購
    order_type = Fields.StringProperty(verbose_name=u'訂購方式')
    order_type_value = Fields.IntegerProperty(verbose_name=u'訂購方式(值)')

    @classmethod
    def get(cls, user, sku, order_type_value=0):
        return cls.query(cls.sku==sku.key, cls.user==user.key, cls.order_type_value==order_type_value).get()

    @classmethod
    def get_or_create(cls, user, sku, quantity=0, order_type_value=0):
        product = sku.product_object.get()
        item = cls.query(cls.sku==sku.key, cls.user==user.key, cls.order_type_value==order_type_value).get()
        if item is None:
            item = cls()
            item.sku = sku.key
            item.user = user.key
            item.order_type_value = order_type_value
            if order_type_value == 0:
                item.order_type = u'現貨'
            else:
                item.order_type = u'預購'
        item._sku = sku
        item._product = product
        item.title = product.title
        item.product_no = product.product_no
        item.product_image = product.image
        item.product_name = product.name
        item.sku_full_name = sku.sku_full_name
        item.spec_full_name = sku.spec_full_name
        item.change_quantity(quantity)
        item.put()
        return item

    @classmethod
    def all_with_user(cls, user):
        key = None
        if user is not None:
            key = user.key
        return cls.query(cls.user==key).order(-cls.sort)

    @classmethod
    def all_with_target(cls, target):
        from argeweb.core.ndb import encode_key
        sku_instance_list = []
        for item in cls.query(cls.temporary==target).order(-cls.sort):
            sku_name = encode_key(item.sku)
            sku_target = None
            for sku_item in sku_instance_list:
                if sku_item['name'] == sku_name:
                    sku_target = sku_item

            if sku_target is None:
                sku_target = {
                    'name': sku_name,
                    'sku': item.sku_instance,
                    'need_stock_out_quantity': item.quantity,
                    'need_stock_in_quantity': 0
                }
                sku_instance_list.append(sku_target)
            else:
                sku_target['need_stock_out_quantity'] += item.quantity
            sku_quantity = sku_target['sku'].quantity
            if sku_target['need_stock_out_quantity'] >= sku_quantity:
                sku_target['need_stock_in_quantity'] = sku_target['need_stock_out_quantity'] - sku_quantity
        return sku_instance_list

    @classmethod
    def before_delete(cls, key):
        item = key.get()
        if item.order_type_value == 0:
            if item.quantity > 0:
                sku = item.sku.get()
                sku.estimate = sku.estimate - item.quantity_has_count
                sku.put()

    @classmethod
    def create_from_order_item(cls, order_item, temporary_key):
        item = cls()
        for p in order_item._properties:
            setattr(item, p, getattr(order_item, p))
        item.temporary = temporary_key
        item.put()
        return item

    @property
    def sku_instance(self):
        if not hasattr(self, '_sku'):
            self._sku = self.sku.get()
        return self._sku

    @property
    def product_instance(self):
        if not hasattr(self, '_product'):
            self._product = self.sku_instance.product_object.get()
        return self._product

    def change_quantity(self, quantity):
        sku = self.sku_instance
        product = self.product_instance
        if sku.use_price:
            self.price = sku.price
        else:
            self.price = product.price
        if sku.use_cost:
            self.cost = sku.cost
        else:
            self.cost = product.cost
        if self.order_type_value == 0:
            config = ProductConfigModel.find_by_product(product)
            if config.stock_recover:
                self.expired_time = time() + config.stock_recover_time
            else:
                self.expired_time = time() + 525600
            can_use_quantity = sku.quantity - sku.estimate + int(self.quantity_has_count)
            old_quantity_has_count = self.quantity_has_count
            if can_use_quantity >= quantity and product.can_order:
                self.can_add_to_order = True
                self.quantity = quantity
                self.quantity_has_count = quantity
            else:
                self.can_add_to_order = False
                self.quantity = 0
                self.quantity_has_count = 0
            sku.estimate = sku.estimate - abs(old_quantity_has_count) + abs(self.quantity)
            sku.put()
        else:
            if product.can_pre_order:
                self.can_add_to_order = True
                self.quantity = quantity
            else:
                self.can_add_to_order = False
                self.quantity = 0
            sku.pre_order_quantity = sku.pre_order_quantity - abs(int(self.quantity_has_count)) + abs(self.quantity)
            sku.put()

    def quantity_can_be_order(self, user=None, sku=None):
        if sku is None:
            sku = self.sku.get()
        if self.order_type_value > 0:
            return 999
        if user:
            if self.quantity is not None:
                if (sku.quantity - sku.estimate + self.quantity) > 0:
                    return sku.quantity - sku.estimate + self.quantity
        if (sku.quantity - sku.estimate) > 0:
            return sku.quantity - sku.estimate
        return 0