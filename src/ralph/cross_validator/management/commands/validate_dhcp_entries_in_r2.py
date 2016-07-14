# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from ralph.admin.helpers import getattr_dunder
from ralph.cross_validator.ralph2.networks import DHCPEntry
from ralph.cross_validator.ralph2.components import Ethernet
from ralph.cross_validator.ralph2.device import IPAddress

logger = logging.getLogger(__name__)


def generate_row(obj, *args):
    for arg in args:
        yield(str(getattr_dunder(obj, arg, '<empty>')))


def mismatch_devices(mac, ip, eth_device, ip_device):
    if eth_device != ip_device and eth_device and ip_device:  # noqa
        fields = ['id', 'name', 'venture__name', 'venture__department__name']  # noqa
        if eth_device:
            eth_row = generate_row(eth_device, *fields)
        else:
            eth_row = ['<empty>'] * len(fields)
        if ip_device:
            ip_row = generate_row(ip_device, *fields)
        else:
            ip_row = ['<empty>'] * len(fields)
        row = [mac, ip]
        row.extend(eth_row)
        row.extend(ip_row)
        print('\t'.join(row))


class Command(BaseCommand):
    def handle(self, *args, **options):
        dhcp = DHCPEntry.objects.all().values_list('mac', 'ip')
        results = []
        print('Generating list of MACs, IPs and devices')
        for mac, ip in dhcp:
            try:
                eth_device = Ethernet.objects.get(mac=mac).device
            except Ethernet.DoesNotExist:
                eth_device = 0
            try:
                ip_device = IPAddress.objects.get(address=ip).device
            except IPAddress.DoesNotExist:
                ip_device = 0
            results.append((mac, ip, eth_device, ip_device))

        print('Mismatch devices')
        for mac, ip, eth_device, ip_device in results:
            mismatch_devices(mac, ip, eth_device, ip_device)
