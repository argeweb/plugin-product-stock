#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product.models.product_model import ProductModel, ProductCategoryModel
from plugins.application_user.models.application_user_model import ApplicationUserModel


class StockHistoryModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
            'sku_full_name': u'sku 編號'
        }

    user = Fields.CategoryProperty(verbose_name=u'使用者')
    user_name = Fields.StringProperty(verbose_name=u'使用者名稱')
    status = Fields.StringProperty(verbose_name=u'狀態')
    operation_from = Fields.StringProperty(verbose_name=u'操作類型') # 產品出入庫、訂單出貨、日常調動

