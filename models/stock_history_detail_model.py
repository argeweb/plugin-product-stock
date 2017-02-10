#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product.models.product_model import ProductModel, ProductCategoryModel
from stock_history_model import StockHistoryModel


class StockHistoryDetailModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
        }

    history = Fields.CategoryProperty(verbose_name=u'歷史記錄', kind=StockHistoryModel)
    product_name = Fields.StringProperty(verbose_name=u'產品名稱')
    spec_full_name = Fields.StringProperty(verbose_name=u'完整規格名稱')
    sku_full_name = Fields.StringProperty(verbose_name=u'sku 編號')
    operation_type = Fields.StringProperty(verbose_name=u'操作類型')  # 出庫、入庫、轉倉
    warehouse = Fields.CategoryProperty(verbose_name=u'倉庫')
    warehouse_target = Fields.CategoryProperty(verbose_name=u'目標倉庫')
    quantity = Fields.IntegerProperty(verbose_name=u'數量')
