# -*- coding: utf-8 -*-
import ipaddress
import logging
import os
import pickle
from functools import partial
from itertools import chain

from django.core.management.base import BaseCommand

from ralph.admin.helpers import getattr_dunder
from ralph.cross_validator.ralph2.networks import DHCPEntry
from ralph.cross_validator.ralph2.components import Ethernet
from ralph.cross_validator.ralph2.device import (
    Device,
    IPAddress
)

logger = logging.getLogger(__name__)

print_row = partial(print, sep='\t')

all_macs = []


def generate_row(obj, *args):
    for arg in args:
        yield(str(getattr_dunder(obj, arg, '<empty>')))


def mismatch_devices(mac, ip, eth_device, ip_device):
    if eth_device != ip_device and eth_device and ip_device:  # noqa
        all_macs.append(mac)
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
        print_row('\t'.join(row))


def deleted_devices_with_entry_in_dhcp(mac, ip, eth_device, ip_device):
    fields = ['id', 'name', 'venture__name', 'venture__department__name']
    if eth_device and eth_device.deleted or ip_device and ip_device.deleted:
        all_macs.append(mac)
        row = [mac, ip]
        row.extend(generate_row(eth_device or eth_device, *fields))
        print_row(*row)


def entry_without_device(mac, ip, eth_device, ip_device):
    if not eth_device and not ip_device:
        all_macs.append(mac)
        print_row(mac, ip, eth_device, ip_device)


def entries_on_stock(mac, ip, eth_device, ip_device, devices_on_stock):
    fields = ['id', 'name', 'venture__name', 'venture__department__name']
    if eth_device in devices_on_stock or ip_device in devices_on_stock:
        all_macs.append(mac)
        row = [mac, ip]
        row.extend(generate_row(eth_device or eth_device, *fields))
        print_row(*row)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--stock-ventures',
            dest='stock_ventures',
            action='append',
            type=int,
        )
        parser.add_argument(
            '--stock-services',
            dest='stock_services',
            action='append',
            type=int,
        )
        parser.add_argument(
            '--use-cache',
            dest='cache',
            action='store_true',
        )
        parser.add_argument(
            '--ignore-network',
            dest='ignored_network',
            type=ipaddress.IPv4Network
        )

    def handle(self, *args, **options):
        ignored_network = options['ignored_network']

        dhcp = []
        if options['cache']:
            with open('dhcp_entries.txt', 'r') as f:
                dhcp = [
                    item.split()
                    for item in f.read().splitlines()
                    if ipaddress.IPv4Address(item.split()[1]) not in ignored_network  # noqa
                ]
        else:
            dhcp = DHCPEntry.objects.all().values_list('mac', 'ip')
            with open('dhcp_entries.txt', 'w') as f:
                for mac, ip in dhcp:
                    if ipaddress.IPv4Address(ip) in ignored_network:
                        continue
                    f.write('{} {}\n'.format(mac, ip))
        results = []
        print('Generating list of MACs, IPs and devices')
        if options['cache']:
            with open('cache.pickle', 'rb') as f:
                results = pickle.load(f)
        else:
            for mac, ip in dhcp:
                if ipaddress.IPv4Address(ip) in ignored_network:
                    continue
                try:
                    eth_device = Ethernet.objects.get(mac=mac).device
                except Ethernet.DoesNotExist:
                    eth_device = 0
                try:
                    ip_device = IPAddress.objects.get(address=ip).device
                except IPAddress.DoesNotExist:
                    ip_device = 0
                results.append((mac, ip, eth_device, ip_device))
            with open('cache.pickle', 'wb') as f:
                pickle.dump(results, f, pickle.HIGHEST_PROTOCOL)

        self.stdout.write(
            self.style.NOTICE('Mismatch devices')
        )
        for mac, ip, eth_device, ip_device in results:
            mismatch_devices(mac, ip, eth_device, ip_device)

        self.stdout.write(
            self.style.NOTICE('Deleted devices with entry in DHCP')
        )
        for mac, ip, eth_device, ip_device in results:
            deleted_devices_with_entry_in_dhcp(mac, ip, eth_device, ip_device)

        self.stdout.write(
            self.style.NOTICE('Entries without devices')
        )
        for mac, ip, eth_device, ip_device in results:
            entry_without_device(mac, ip, eth_device, ip_device)

        if options['stock_ventures'] or options['stock_services']:
            self.stdout.write(
                self.style.NOTICE('Entries on stock')
            )
            ventures = options.get('stock_ventures', [])
            services = options.get('stock_services', [])

            devices_on_stock = list(chain(
                Device.objects.filter(service_id__in=services) if services else [],  # noqa
                Device.objects.filter(venture_id__in=ventures) if ventures else []  # noqa
            ))
            for mac, ip, eth_device, ip_device in results:
                entries_on_stock(
                    mac, ip, eth_device, ip_device, devices_on_stock
                )

        self.stdout.write(
            self.style.NOTICE('Set of MACs')
        )
        print(*set(all_macs), sep='\n')

