# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.menu import MenuItem

from ralph.menu import Menu


class CMDBMenu(Menu):
    module = MenuItem(
        'CMDB',
        name='module_cmdb',
        fugue_icon='fugue-thermometer',
        href='/cmdb/changes/timeline',
    )

menu_class = CMDBMenu
