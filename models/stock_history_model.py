#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.application_user.models.application_user_model import ApplicationUserModel


class StockHistoryModel(BasicModel):
    class Meta:
        label_name = {
            'is_enable': u'啟用',
            'title': u'完整規格名稱',
            'sku_full_name': u'sku 編號'
        }

    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)
    user_name = Fields.StringProperty(verbose_name=u'使用者名稱')
    status = Fields.BooleanProperty(verbose_name=u'狀態')
    result = Fields.StringProperty(verbose_name=u'結果訊息')
    operation = Fields.StringProperty(verbose_name=u'操作類型') # 產品出入庫、訂單出貨、日常調動
    remake = Fields.StringProperty(verbose_name=u'摘要')

    @property
    def details(self):
        from stock_history_detail_model import StockHistoryDetailModel as Detail
        return Detail.query(Detail.history == self.key).order(-Detail.sort)


def create_history(user, operation, remake=u'', status=True, result=u'完成'):
    r = StockHistoryModel()
    r.user = user.key
    r.user_name = user.name
    r.status = status
    r.operation = operation
    r.result = result
    r.remake = remake
    r.put()
    return r
