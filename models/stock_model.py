#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product.models.product_model import ProductModel, ProductCategoryModel


class StockModel(BasicModel):
    class Meta:
        label_name = {
            'name': u'名稱',
            'content': u'詳細介紹',
            'price':u'價格',
            'quantity':u'庫存數量',
            'color':u'顏色',
            'description':u'簡介',
            'info':u'規格說明',
            'spec_name_1':u'尺寸/容量',
            'image': u'圖片',
            'is_enable': u'啟用',
            'category': u'產品',
        }
    name = Fields.StringProperty()
    price = Fields.FloatProperty()
    color = Fields.StringProperty()
    spec_name_1 = Fields.StringProperty()
    quantity = Fields.FloatProperty()
    category = Fields.CategoryProperty(required=True, kind=ProductModel)

    @classmethod
    def all_enable(cls, category=None, *args, **kwargs):
        cat = None
        if category:
            cat = ProductCategoryModel.find_by_name(category)
        if cat is None:
            return cls.query(cls.is_enable==True).order(-cls.sort)
        else:
            return cls.query(cls.category==cat.key, cls.is_enable==True).order(-cls.sort)
