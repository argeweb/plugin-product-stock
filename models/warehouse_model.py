#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields


class WarehouseModel(BasicModel):
    name = Fields.HiddenProperty(verbose_name=u'識別名稱')
    title = Fields.StringProperty(verbose_name=u'倉庫名稱')
    address = Fields.StringProperty(verbose_name=u'地址')
    telephone = Fields.StringProperty(verbose_name=u'電話')

    def stock_in(self, sku, quantity, history, detail_remark):
        from stock_keeping_unit_in_warehouse_model import StockKeepingUnitInWarehouseModel
        from ..models.stock_history_detail_model import create_history_detail
        create_history_detail(history, sku, detail_remark, quantity, self)
        return StockKeepingUnitInWarehouseModel.stock_in(self, sku, quantity)

    def stock_out(self, sku, quantity, history, detail_remark, auto_fill=False):
        from stock_keeping_unit_in_warehouse_model import StockKeepingUnitInWarehouseModel
        from ..models.stock_history_detail_model import create_history_detail
        create_history_detail(history, sku, detail_remark, quantity, self)
        return StockKeepingUnitInWarehouseModel.stock_out(self, sku, quantity, auto_fill)

    def stock_out_check(self, sku, quantity, auto_fill=False):
        from stock_keeping_unit_in_warehouse_model import StockKeepingUnitInWarehouseModel
        return StockKeepingUnitInWarehouseModel.stock_out_check(self, sku, quantity, auto_fill)

