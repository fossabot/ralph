from django.db import models

from ralph.cross_validator.ralph2 import generate_meta
from ralph.cross_validator.ralph2.device import Device


class Component(models.Model):
    device = models.ForeignKey(Device)

    class Meta:
        abstract = True


class Ethernet(Component):
    mac = models.CharField(max_length=32, unique=True)

    class Meta(generate_meta(app_label='discovery', model_name='ethernet')):
        pass
