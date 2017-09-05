# -*- coding: utf-8 -*-
import logging
import textwrap

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ralph.dashboards.models import Graph
from ralph.lib.metrics import build_statsd_client

logger = logging.getLogger(__name__)
PREFIX = settings.STATSD_GRAPHS_PREFIX
PATH = '{{}}.{{}}'.format(PREFIX)


def normalize(s):
    s = slugify(s)
    return s.replace('-', '_')


class Command(BaseCommand):
    """Push to statsd data generated by graphs."""
    help = textwrap.dedent(__doc__).strip()

    def handle(self, *args, **kwargs):
        statsd = build_statsd_client(prefix=settings.STATSD_GRAPHS_PREFIX)
        graphs = Graph.objects.filter(push_to_statsd=True)
        for graph in graphs:
            graph_data = graph.get_data()
            graph_name = normalize(graph.name)
            for label, value in zip(graph_data['labels'], graph_data['series']):
                path = PATH.format(graph_name, normalize(label))
                statsd.gauge(path, value)
