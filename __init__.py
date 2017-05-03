#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/07/08.

from argeweb import ViewDatastore

plugins_helper = {
    'title': u'產品庫存',
    'desc': u'擴增產品的庫存功能',
    'controllers': {
        'stock': {
            'group': u'庫存管理',
            'actions': [
                {'action': 'list', 'name': u'最小庫存單位'},
                {'action': 'add', 'name': u'新增產品庫存'},
                {'action': 'edit', 'name': u'編輯產品庫存'},
                {'action': 'view', 'name': u'檢視產品庫存'},
                {'action': 'delete', 'name': u'刪除產品庫存'},
                {'action': 'plugins_check', 'name': u'啟用停用模組'},
            ]
        },
        'warehouse': {
            'group': u'倉庫設置',
            'actions': [
                {'action': 'list', 'name': u'倉庫列表'},
                {'action': 'add', 'name': u'新增倉庫'},
                {'action': 'edit', 'name': u'編輯倉庫'},
                {'action': 'view', 'name': u'檢視倉庫'},
                {'action': 'delete', 'name': u'刪除倉庫'},
            ]
        },
        'stock_request': {
            'group': u'出入庫請求',
            'actions': [
                {'action': 'list', 'name': u'請求列表'},
                {'action': 'add', 'name': u'新增請求'},
                {'action': 'edit', 'name': u'編輯請求'},
                {'action': 'view', 'name': u'檢視請求'},
                {'action': 'delete', 'name': u'刪除請求'},
            ]
        }
    }
}
