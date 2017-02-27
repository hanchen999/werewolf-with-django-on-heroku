# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from channels import Channel
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    gameStart = models.IntegerField(default=0)
    playerNumber = models.IntegerField(default=0)
    currentNumber = models.IntegerField(default=0)
    roleList = models.TextField(default='')
    voteList = models.TextField(default='')
    jinghui = models.IntegerField(default=1)
    daystatus = models.IntegerField(default=0)
    duyao = models.IntegerField(default=1)
    jieyao = models.IntegerField(default=1)
    deadman = models.IntegerField(default=0)
    def __unicode__(self):
        return self.label


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    handle = models.TextField()
    message = models.TextField()
    typo = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')
    
    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'typo': self.typo, 'timestamp': self.formatted_timestamp}

class Player(models.Model):
    room = models.ForeignKey(Room, related_name='players')
    position = models.SlugField(unique=True)
    address = models.TextField()
    jingzhang = models.IntegerField(default=0)
    identification = models.IntegerField(default=-1)
    alive = models.IntegerField(default=1)
    def __unicode__(self):
        return '{position}: {address}'.format(**self.as_dict())
    def as_dict(self):
        return {'position': self.position, 'address': self.address}
