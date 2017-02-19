#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product.models.product_model import ProductModel, ProductCategoryModel


class StockKeepingUnitModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
            'sku_full_name': u'sku 編號'
        }

    @property
    def sku_full_name(self):
        sku_prev_name = u''
        if self.sku_prev_name is not u'' and self.sku_prev_name is not None:
            sku_prev_name = '%s-' % self.sku_prev_name
        sku_post_name = u''
        if self.name is not u'' and self.name is not None:
            sku_post_name = self.name
        if self.sku_no is not u'' and self.sku_no is not None:
            sku_post_name = self.sku_no
        return '%s%s' % (sku_prev_name, sku_post_name)

    spec_full_name = Fields.StringProperty(verbose_name=u'完整規格名稱')
    quantity = Fields.IntegerProperty(verbose_name=u'現存數量', default=0)
    quantity_in_order = Fields.IntegerProperty(verbose_name=u'訂單預估數量', default=0)
    low_stock_quantity = Fields.IntegerProperty(verbose_name=u'庫存警戒線', default=-1)
    last_in_quantity = Fields.IntegerProperty(verbose_name=u'最後入庫數量', default=0)
    last_in_datetime = Fields.DateTimeProperty(verbose_name=u'最後入庫時間', auto_now_add=True)
    last_out_quantity = Fields.IntegerProperty(verbose_name=u'最後出庫數量', default=0)
    last_out_datetime = Fields.DateTimeProperty(verbose_name=u'最後入庫時間', auto_now_add=True)

    name = Fields.StringProperty(verbose_name=u'系統編號')
    sku_no = Fields.StringProperty(verbose_name=u'sku 編號')
    sku_prev_name = Fields.HiddenProperty(verbose_name=u'sku 前置編號')
    is_enable = Fields.BooleanProperty(verbose_name=u'顯示於前台', default=True)
    can_be_purchased = Fields.BooleanProperty(verbose_name=u'可購買', default=True)

    use_automatic_increment = Fields.BooleanProperty(verbose_name=u'自動增量', default=False)
    automatic_increment_quantity = Fields.IntegerProperty(verbose_name=u'增量的數量', default=0)
    category = Fields.KeyProperty(verbose_name=u'所屬產品', kind=ProductModel)
    spec_name_1 = Fields.HiddenProperty(verbose_name=u'規格名稱 1')
    spec_name_2 = Fields.HiddenProperty(verbose_name=u'規格名稱 2')
    spec_name_3 = Fields.HiddenProperty(verbose_name=u'規格名稱 3')
    spec_name_4 = Fields.HiddenProperty(verbose_name=u'規格名稱 4')
    spec_name_5 = Fields.HiddenProperty(verbose_name=u'規格名稱 5')
    spec_value_1 = Fields.HiddenProperty(verbose_name=u'規格值 1')
    spec_value_2 = Fields.HiddenProperty(verbose_name=u'規格值 2')
    spec_value_3 = Fields.HiddenProperty(verbose_name=u'規格值 3')
    spec_value_4 = Fields.HiddenProperty(verbose_name=u'規格值 4')
    spec_value_5 = Fields.HiddenProperty(verbose_name=u'規格值 5')
    # TODO 庫存變動時的歷史記錄

    def before_put(self):
        sku_prev_name = u''
        cat = self.category
        if cat is not None:
            try:
                cat = cat.get()
                sku_prev_name = cat.sku_prev_name
            except:
                pass
        spec_list = (u'%s' % self.spec_full_name).split(u',')
        i = 0
        setattr(self, 'sku_prev_name', sku_prev_name)
        for index in xrange(0, len(spec_list)):
            spec = spec_list[index].split(u':')
            setattr(self, 'spec_name_%s' % (index + 1), spec[0])
            setattr(self, 'spec_value_%s' % (index + 1), spec[1])

    @property
    def title(self):
        return self.spec_full_name

    @property
    def p_quantity(self):
        quantity = self.quantity if self.quantity is not None else 0
        last_in_quantity = self.last_in_quantity if self.last_in_quantity is not None else 0
        if last_in_quantity == 0:
            return 0
        if last_in_quantity < self.low_stock_quantity:
            last_in_quantity = self.low_stock_quantity
        return int((float(quantity) / float(last_in_quantity)) * 10000) / 100.0

    @property
    def is_low_stock_level(self):
        quantity = self.quantity if self.quantity is not None else 0
        low_stock_quantity = self.low_stock_quantity if self.low_stock_quantity is not None else -1
        return quantity <= low_stock_quantity

    @classmethod
    def all_enable(cls, category=None, *args, **kwargs):
        cat = None
        if category:
            cat = ProductCategoryModel.find_by_name(category)
        if cat is None:
            return cls.query(cls.is_enable==True).order(-cls.sort)
        else:
            return cls.query(cls.category==cat.key, cls.is_enable==True).order(-cls.sort)
