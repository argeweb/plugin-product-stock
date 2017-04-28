#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.application_user.models.application_user_model import ApplicationUserModel
from plugins.order.models.order_model import OrderModel


class StockHistoryModel(BasicModel):
    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)
    user_name = Fields.StringProperty(verbose_name=u'使用者名稱')
    status = Fields.BooleanProperty(verbose_name=u'狀態')  # True 成功, False 失敗
    result = Fields.StringProperty(verbose_name=u'結果訊息')
    operation = Fields.StringProperty(verbose_name=u'操作類型') # 產品出入庫、訂單出貨、日常調動
    remake = Fields.StringProperty(verbose_name=u'摘要')
    order = Fields.KeyProperty(verbose_name=u'所屬訂單', kind=OrderModel)
    temporary_key = Fields.StringProperty(verbose_name=u'訂單暫存序號')
    temporary_items = Fields.SidePanelProperty(verbose_name=u'相關項目', text=u'點擊此處查看 相關項目', auto_open=True,
                                        uri='admin:product_stock:stock:side_panel_for_order')

    @property
    def details(self):
        from stock_history_detail_model import StockHistoryDetailModel
        return StockHistoryDetailModel.all_with_history(self)


def create_history(user, operation, remake=u'', status=True, result=u'完成', order=None):
    r = StockHistoryModel()
    r.user = user.key
    r.user_name = user.name
    r.status = status
    r.operation = operation
    if order is not None:
        r.order = order.key
    r.result = result
    r.remake = remake
    r.put()
    return r
