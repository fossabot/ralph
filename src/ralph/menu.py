# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from bob.menu import MenuItem
from ralph.account.models import Perm


class Menu(object):
    module = None

    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs
        profile = self.request.user.get_profile()
        self.has_perm = profile.has_perm

    def get_module(self):
        if not self.module:
            raise ImproperlyConfigured(
                'Menu required definition of \'module\' or an implementation '
                'of \'get_module()\'')

        if not isinstance(self.module, MenuItem):
            raise ImproperlyConfigured(
                'Module must inheritence from \'MenuItem\'')

        return self.module

    def get_submodules(self):
        return []

    def get_actions_or_tabs(self, submodule):
        return []


class CoreMenu(Menu):
    module = MenuItem(
        'Core',
        name='module_core',
        fugue_icon='fugue-store',
        view_name='ventures',
    )

    def __init__(self, *args, **kwargs):
        self.venture = None
        self.object = None
        super(CoreMenu, self).__init__(*args, **kwargs)

    def get_submodules(self):
        venture = (
            self.venture if self.venture and self.venture != '*' else None
        ) or (
            self.object.venture if self.object else None
        )

        submodules = [
            MenuItem(
                'Ventures',
                fugue_icon='fugue-store',
                view_name='ventures',
            )
        ]
        if self.has_perm(Perm.read_dc_structure):
            submodules.append(
                MenuItem('Racks', fugue_icon='fugue-building',
                         view_name='racks'))
        if self.has_perm(Perm.read_network_structure):
            submodules.append(
                MenuItem('Networks', fugue_icon='fugue-weather-clouds',
                         view_name='networks'))
        if self.has_perm(Perm.read_device_info_reports):
            submodules.append(
                MenuItem('Reports', fugue_icon='fugue-report',
                         view_name='reports'))
        submodules.append(
            MenuItem('Ralph CLI', fugue_icon='fugue-terminal',
                     href='#beast'))
        submodules.append(
            MenuItem('Quick scan', fugue_icon='fugue-radar',
                     href='#quickscan'))
        # if self.has_perm(Perm.read_device_info_generic, venture):
        #     submodules.extend([
        #         MenuItem('Info', fugue_icon='fugue-wooden-box',
        #                  href=self.tab_href('info')),
        #         MenuItem('Components', fugue_icon='fugue-box',
        #                  href=self.tab_href('components')),
        #         MenuItem('Software', fugue_icon='fugue-disc',
        #                  href=self.tab_href('software')),
        #         MenuItem('Addresses', fugue_icon='fugue-network-ip',
        #                  href=self.tab_href('addresses')),
        #     ])
        # if self.has_perm(Perm.edit_device_info_financial, venture):
        #     submodules.extend([
        #         MenuItem('Prices', fugue_icon='fugue-money-coin',
        #                  href=self.tab_href('prices')),
        #     ])
        # if self.has_perm(Perm.read_device_info_financial, venture):
        #     submodules.extend([
        #         MenuItem('Costs', fugue_icon='fugue-wallet',
        #                  href=self.tab_href('costs')),
        #     ])
        # if self.has_perm(Perm.read_device_info_history, venture):
        #     submodules.extend([
        #         MenuItem('History', fugue_icon='fugue-hourglass',
        #                  href=self.tab_href('history')),
        #     ])

        # if ('ralph.scan' in settings.INSTALLED_APPS and
        #         self.has_perm(Perm.edit_device_info_generic) and
        #         self.kwargs.get('device')):
        #     submodules.extend([
        #         MenuItem(
        #             'Scan',
        #             name='scan',
        #             fugue_icon='fugue-flashlight',
        #             href=self.tab_href('scan'),
        #         ),
        #     ])
        # if ('ralph.cmdb' in settings.INSTALLED_APPS and
        #         self.has_perm(Perm.read_configuration_item_info_generic)):
        #     ci = ''
        #     device_id = self.kwargs.get('device')
        #     if device_id:
        #         deleted = False
        #         if self.request.GET.get('deleted', '').lower() == 'on':
        #             deleted = True
        #         try:
        #             if deleted:
        #                 device = Device.admin_objects.get(pk=device_id)
        #             else:
        #                 device = Device.objects.get(pk=device_id)
        #             ci = CI.get_by_content_object(device)
        #         except Device.DoesNotExist:
        #             pass
        #     if ci:
        #         submodules.extend([
        #             MenuItem(
        #                 'CMDB', fugue_icon='fugue-thermometer',
        #                 href='/cmdb/ci/view/%s' % ci.id
        #             ),
        #         ])
        # if self.has_perm(Perm.read_device_info_reports, venture):
        #     submodules.extend([
        #         MenuItem('Reports', fugue_icon='fugue-reports-stack',
        #                  href=self.tab_href('reports')),
        #     ])
        # if details == 'bulkedit':
        #     submodules.extend([
        #         MenuItem('Bulk edit', fugue_icon='fugue-pencil-field',
        #                  name='bulkedit'),
        #     ])
        return submodules

    def get_actions_or_tabs(self, submodule):
        pass

menu_class = CoreMenu
# module = MenuItem(
#     'Core',
#     name='module_core',
#     fugue_icon='fugue-store',
#     view_name='ventures',
# )

# submenu_items = [
#     MenuItem('Ventures', fugue_icon='fugue-store',
#              view_name='ventures')
# ]
# if self.has_perm(Perm.read_dc_structure):
#     submenu_items.append(
#         MenuItem('Racks', fugue_icon='fugue-building',
#                  view_name='racks'))
# if self.has_perm(Perm.read_network_structure):
#     submenu_items.append(
#         MenuItem('Networks', fugue_icon='fugue-weather-clouds',
#                  view_name='networks'))
# if self.has_perm(Perm.read_device_info_reports):
#     submenu_items.append(
#         MenuItem('Reports', fugue_icon='fugue-report',
#                  view_name='reports'))
# submenu_items.append(
#     MenuItem('Ralph CLI', fugue_icon='fugue-terminal',
#              href='#beast'))
# submenu_items.append(
#     MenuItem('Quick scan', fugue_icon='fugue-radar',
#              href='#quickscan'))

