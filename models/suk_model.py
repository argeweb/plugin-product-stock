#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product.models.product_model import ProductModel, ProductCategoryModel




class StockKUModel(BasicModel):
    name = Fields.StringProperty(verbose_name=u'系統編號')

    title = Fields.StringProperty(verbose_name=u'最小庫存單位名稱')
    spec_name_1 = Fields.StringProperty(verbose_name=u'規格名稱 1')
    spec_name_2 = Fields.StringProperty(verbose_name=u'規格名稱 2')
    spec_name_3 = Fields.StringProperty(verbose_name=u'規格名稱 3')
    spec_name_4 = Fields.StringProperty(verbose_name=u'規格名稱 4')
    spec_name_5 = Fields.StringProperty(verbose_name=u'規格名稱 5')
    spec_name_6 = Fields.StringProperty(verbose_name=u'規格名稱 6')
    spec_name_7 = Fields.StringProperty(verbose_name=u'規格名稱 7')
    spec_name_8 = Fields.StringProperty(verbose_name=u'規格名稱 8')
    spec_value_1 = Fields.StringProperty(verbose_name=u'規格值 1')
    spec_value_2 = Fields.StringProperty(verbose_name=u'規格值 2')
    spec_value_3 = Fields.StringProperty(verbose_name=u'規格值 3')
    spec_value_4 = Fields.StringProperty(verbose_name=u'規格值 4')
    spec_value_5 = Fields.StringProperty(verbose_name=u'規格值 5')
    spec_value_6 = Fields.StringProperty(verbose_name=u'規格值 6')
    spec_value_7 = Fields.StringProperty(verbose_name=u'規格值 7')
    spec_value_8 = Fields.StringProperty(verbose_name=u'規格值 8')

    totoal_income = Fields.FloatProperty(verbose_name=u'總入庫數量')
    totoal_exout = Fields.FloatProperty(verbose_name=u'總出庫數量')
    totoal = Fields.FloatProperty(verbose_name=u'總在庫數量')
    custom_product_code = Fields.FloatProperty(verbose_name=u'自定代碼(自訂條碼)')
    universal_product_code = Fields.FloatProperty(verbose_name=u'通用產品代碼(條碼)')

    price = Fields.FloatProperty()
    color = Fields.StringProperty()
    quantity = Fields.FloatProperty()
    category = Fields.CategoryProperty(required=True, kind=ProductModel)
    # TODO 庫存變動時的歷史記錄

    @classmethod
    def all_enable(cls, category=None, *args, **kwargs):
        cat = None
        if category:
            cat = ProductCategoryModel.find_by_name(category)
        if cat is None:
            return cls.query(cls.is_enable==True).order(-cls.sort)
        else:
            return cls.query(cls.category==cat.key, cls.is_enable==True).order(-cls.sort)
