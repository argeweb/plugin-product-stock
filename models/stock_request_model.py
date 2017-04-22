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


class StockRequestModel(BasicModel):
    create_user = Fields.KeyProperty(verbose_name=u'請求建立者', kind=ApplicationUserModel)
    authorizing_officer = Fields.KeyProperty(verbose_name=u'評核人員', kind=ApplicationUserModel)
    reviewing_officer = Fields.KeyProperty(verbose_name=u'復核人員', kind=ApplicationUserModel)

    order = Fields.KeyProperty(verbose_name=u'所屬訂單', kind=OrderModel)
    request_type = Fields.StringProperty(verbose_name=u'請求類型') # 出庫、入庫、盤點
    source_type = Fields.StringProperty(verbose_name=u'請求類型') # 訂單全部、訂單庫存、訂單預購、手動輸入
    remake = Fields.StringProperty(verbose_name=u'摘要')

    @property
    def details(self):
        from stock_history_detail_model import StockHistoryDetailModel as Detail
        return Detail.query(Detail.history == self.key).order(-Detail.sort)

    @classmethod
    def all_with_request_type(cls, request_type=None, *args, **kwargs):
        if request_type is None:
            return cls.query().order(-cls.sort)
        return cls.query(cls.request_type==request_type).order(-cls.sort)
