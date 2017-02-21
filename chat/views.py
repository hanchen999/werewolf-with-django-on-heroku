import random
import string
from django.db import transaction
from django.shortcuts import render, redirect
import haikunator
from .models import Room

def about(request):
    return render(request, "chat/about.html")

def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    while not new_room:
        with transaction.atomic():
            label = haikunator.haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room = Room.objects.create(label=label)
    return redirect(chat_room, label=label)

def create_room(request):
    #Create a new room for lang ren sha
    #
    if request.method == 'GET':
        return render(request, "chat/create_room.html", {})
    else:
        label = request.form.get['id']
        playNumber = 0
        roleList = request.form.get['cunmin'] + ',' + request.form.get['langren']
        playNumber += int(request.form.get['cunmin']) + int(request.form.get['langren'])
        if request.form.get['yuyanjia']:
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.form.get['nvwu']:
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.form.get['lieren']:
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.form.get['shouwei']:
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        gameStart = 0
    return redirect(chat_room, label=label, playNumber=playNumber, gameStart=gameStart, roleList=roleList)
def join_room(request):
    #Create a new room for lang ren sha
    #
    new_room = None
    return redirect(chat_room, label=label)

def chat_room(request):
    """
    Room view - show the room, with latest messages.

    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label, playNumber=playNumber, gameStart=gameStart, roleList=roleList)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chat/room.html", {
        'room': room,
        'messages': messages,
    })
