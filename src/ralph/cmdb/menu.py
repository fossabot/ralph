# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.menu import MenuItem

# from ralph.account.models import Perm
from ralph.menu import Menu


class CMDBMenu(Menu):
    module = MenuItem(
        'CMDB',
        name='module_cmdb',
        fugue_icon='fugue-thermometer',
        href='/cmdb/changes/timeline',
    )

menu_class = CMDBMenu

    # def get_submodules(self):
    #     profile = self.request.user.get_profile()
    #     has_perm = profile.has_perm
    #     venture = (
    #         self.venture if self.venture and self.venture != '*' else None
    #     ) or (
    #         self.object.venture if self.object else None
    #     )
