#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Model utilities and mixins."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

from django.db import models as db
from django.utils.translation import ugettext_lazy as _


class LastSeen(db.Model):
    last_seen = db.DateTimeField(verbose_name=_("last seen"),
                                 default=datetime.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        update_last_seen = kwargs.pop('update_last_seen', False)
        if update_last_seen:
            self.last_seen = datetime.now()
        super(LastSeen, self).save(*args, **kwargs)


class SavingUser(db.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.saving_user = kwargs.pop('user', None)
        return super(SavingUser, self).save(*args, **kwargs)
