from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from channels import Channel

class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    gameStart = models.IntegerField(default=0)
    playerNumber = models.IntegerField(default=0)
    roleList = models.TextField(default='')
    def __unicode__(self):
        return self.label


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    handle = models.TextField()
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')
    
    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': self.formatted_timestamp}

class Player(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    position = models.SlugField(unique=True)
    address = models.TextField()
    def __unicode__(self):
        return '{position}: {address}'.format(**self.as_dict())
    def as_dict(self):
        return {'position': self.position, 'address': self.address}
