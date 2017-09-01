import logging
from contextlib import ContextDecorator

from django.conf import settings

STATSD_IS_INSTALLED = False
try:
    from statsd import defaults, StatsClient
    STATSD_IS_INSTALLED = True
except ImportError:
    pass


logger = logging.getLogger(__name__)
statsd = None


# mock statsd client to be able to use it without checking every time
# if collecting metrics is enabled in settings (ex. when decorating a
# function)
class TimerMock(ContextDecorator):
    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return False

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass


class StatsdMockClient(object):
    def __init__(self, *args, **kwargs):
        logger.warning(
            'Statsd not installed or configured - metrics will NOT be '
            'collected'
        )

    def timer(self, *args, **kwargs):
        return TimerMock()

    def _mock(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self._mock


if STATSD_IS_INSTALLED:
    HOST = getattr(settings, 'STATSD_HOST', defaults.HOST)
    PORT = getattr(settings, 'STATSD_PORT', defaults.PORT)
    PREFIX = getattr(settings, 'STATSD_PREFIX', defaults.PREFIX)
    MAXUDPSIZE = getattr(settings, 'STATSD_MAXUDPSIZE', defaults.MAXUDPSIZE)
    IPV6 = getattr(settings, 'STATSD_IPV6', defaults.IPV6)

    def build_statsd_client(
        host=HOST, port=PORT, prefix=PREFIX, maxudpsize=MAXUDPSIZE, ipv6=IPV6
    ):
        return StatsClient(
            host=host,
            port=port,
            prefix=prefix,
            maxudpsize=maxudpsize,
            ipv6=ipv6
        )
else:
    def build_statsd_client(*args, **kwargs):
        return StatsdMockClient()


if statsd is None:
    statsd = build_statsd_client()
