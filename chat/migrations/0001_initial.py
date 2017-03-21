# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-04 17:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handle', models.TextField()),
                ('message', models.TextField()),
                ('typo', models.TextField()),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('label', models.SlugField(unique=True)),
                ('gameStart', models.IntegerField(default=0)),
                ('playerNumber', models.IntegerField(default=0)),
                ('currentNumber', models.IntegerField(default=0)),
                ('roleList', models.TextField(default='')),
                ('voteList', models.TextField(default='')),
                ('jinghui', models.IntegerField(default=1)),
                ('daystatus', models.IntegerField(default=0)),
                ('jieyao', models.IntegerField(default=0)),
                ('duyao', models.IntegerField(default=0)),
                ('deadman', models.TextField(default='')),
                ('shou', models.IntegerField(default=0)),
                ('link', models.TextField(default='')),
                ('thirdteam', models.IntegerField(default=0)),
                ('theft', models.IntegerField(default=-1)),
                ('burycard', models.IntegerField(default=-1)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.SlugField()),
                ('address', models.TextField()),
                ('jingzhang', models.IntegerField(default=0)),
                ('identification', models.IntegerField(default=-1)),
                ('alive', models.IntegerField(default=1)),
                ('link', models.IntegerField(default=-1)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.Room'),
        ),
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='chat.Room'),
        ),
    ]
