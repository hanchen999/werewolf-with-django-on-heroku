# -*- coding: utf-8 -*-
import random
import string
from django.db import transaction
from django.shortcuts import render, redirect
from channels import Group
import haikunator
from .models import Room

def about(request):
    return render(request, "chat/about.html")

def home(request):
    return render(request, "chat/about.html")

# def new_room(request):
#     """
#     Randomly create a new room, and redirect to it.
#     """
#     new_room = None
#     while not new_room:
#         with transaction.atomic():
#             label = haikunator.haikunate()
#             if Room.objects.filter(label=label).exists():
#                 continue
#             new_room = Room.objects.create(label=label)
#     return redirect(chat_room, label=label)

def create_room(request):
    #Create a new room for lang ren sha
    #
    if request.method == 'GET':
        return render(request, "chat/create_room.html", {})
    else:
        label = request.POST['id']
        if Room.objects.filter(label=label).exists():
            room = Room.objects.filter(label=label).first()
            players = room.players.filter().all()
            if len(players) > 0:
                return render(request, "chat/error.html", {'messages' : 'this name has been used'})
            else:
                room.messages.all().delete()
                room.players.all().delete()
                room.delete()
        playNumber = 0
        roleList = request.POST['cunmin'] + ',' + request.POST['langren']
        playNumber = playNumber + int(request.POST['cunmin']) + int(request.POST['langren'])
        if request.POST.get('yuyanjia', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.POST.get('lieren', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.POST.get('nvwu', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.POST.get('shouwei', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        gameStart = 0
        new_room = Room.objects.create(label=label, gameStart=gameStart, playerNumber=playNumber, roleList=roleList)
    return redirect(chat_room, label=label)

def join_room(request):
    #Create a new room for lang ren sha
    #
    if request.method == 'GET':
        return render(request, "chat/join_room.html", {})
    label = request.POST['label']
    position = request.POST['position']
    try:
        room = Room.objects.filter(label=label).first()
        players = room.players.all()
        count = len(players)
        if int(room.playerNumber) is count:
            return render(request, "chat/error.html", {'messages' : 'this room is full'})
        player = room.players.filter(position=position).first()
        if player is not None；
            return render(request, "chat/error.html", {'messages' : 'this position has been occupied'})
        return redirect(chat_room, label=label, position=position)
    except Room.DoesNotExist:
        return render(request, "chat/error.html", {'messages' : 'this room does not exist'})



def chat_room(request, label, position):
    """
    Room view - show the room, with latest messages.

    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room = Room.objects.filter(label=label).first()

    # We want to show the last 50 messages, ordered most-recent-last
    #messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chat/room.html", {
        'room': room,
        'position': position
        'messages': '',
    })
