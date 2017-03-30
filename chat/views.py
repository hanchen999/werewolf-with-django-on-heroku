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

def judgementView(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        return 'Can not find the room'
    cunmin = ''
    langren = ''
    yuyanjia = ''
    nvwu = ''
    shouwei = ''
    lieren = ''
    bailangwang = ''
    qiubite = ''
    daozei = ''
    for player in room.players.all():
        if player.identification == 0:
            cunmin = cunmin + player.position + ' '
        elif player.identification == 1:
            langren = langren + player.position + ' '
        elif player.identification == 2:
            yuyanjia = yuyanjia + player.position + ' '
        elif player.identification == 3:
            lieren = lieren + player.position + ' '
        elif player.identification == 4:
            nvwu = nvwu + player.position + ' '
        elif player.identification == 5:
            shouwei = shouwei + player.position + ' '
        elif player.identification == 6:
            bailangwang = bailangwang + player.position + ' '
        elif player.identification == 7:
            qiubite = qiubite + player.position + ' '
    Info = 'Identification list \n '
    if len(cunmin) > 0:
        Info = Info + '村民: ' + cunmin + '\n '
    if len(langren) > 0:
        Info = Info + '狼人: ' + langren + '\n '
    if len(yuyanjia) > 0:
        Info = Info + '预言家: ' + yuyanjia + '\n '
    if len(lieren) > 0:
        Info = Info + '猎人: ' + lieren + '\n '
    if len(nvwu) > 0:
        Info = Info + '女巫: ' + nvwu + '\n '
        if room.jieyao != 0:
            Info = Info + '女巫解药已经使用！' + '\n '
        if room.duyao != 0:
            Info = Info + '女巫毒药已经使用！对象是: ' + str(room.duyao) + '\n '
    if len(shouwei) > 0:
        Info = Info + '守卫: ' + shouwei + '\n '
        if room.shou != 0:
            Info = Info + '守卫昨天晚上守卫的人是: ' + str(room.shou) + '\n '
    if len(bailangwang) > 0:
        Info = Info + '白狼王: ' + bailangwang + '\n '
    if len(qiubite) > 0:
        Info = Info + '丘比特: ' + qiubite + '\n '
        Info = Info + '丘比特所连的情侣是: ' + room.link + '\n '
    if room.theft != -1:
        Info = Info + '盗贼: ' + str(room.theft) + '\n '
        temp = room.players.filter(position=room.theft).first
        Info = Info + '盗贼拾取的身份是： ' + str(identificationDict[int(temp.identification)]) + '\n '
        Info = Info + '盗贼掩埋的身份是: ' + str(identificationDict[int(room.burycard)]) + '\n '
    if room.thirdteam == 0:
        Info = Info + '不含有第三阵营！' + '\n '
    else:
        Info = Info + '含有第三阵营！' + '\n '
    return Info


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
            players = room.players.filter(connection=True).all()
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
        if request.POST.get('bailangwang', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.POST.get('qiubite', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber + 1
        else:
            roleList = roleList + ',' + '0'
        if request.POST.get('daozei', False):
            roleList = roleList + ',' + '1'
            playNumber = playNumber - 1
        else:
            roleList = roleList + ',' + '0'
        gameStart = 0
        new_room = Room.objects.create(label=label, gameStart=gameStart, playerNumber=playNumber, roleList=roleList)
    return redirect(chat_room, label=label, position=1)

def join_room(request):
    #Create a new room for lang ren sha
    #
    if request.method == 'GET':
        return render(request, "chat/join_room.html", {})
    label = request.POST['label']
    position = request.POST['position']
    try:
        room = Room.objects.filter(label=label).first()
        if room.gameStart == 1:
            return render(request, "chat/error.html", {'messages' : 'Game has started!'})
        players = room.players.filter(connection=True).all()
        count = len(players)
        if int(room.playerNumber) is count:
            return render(request, "chat/error.html", {'messages' : 'this room is full'})
        player = room.players.filter(position=position).first()
        if player is not None:
            return render(request, "chat/error.html", {'messages' : 'this position has been occupied'})
        return redirect(chat_room, label=label, position=position)
    except Room.DoesNotExist:
        return render(request, "chat/error.html", {'messages' : 'this room does not exist'})

def judge_room(request):
    if request.method == 'GET':
        return render(request, "chat/judge_room.html", {})
    label = request.POST['label']
    pwd = request.POST['pwd']
    room = None
    try:
        room = Room.objects.filter(label=label).first()
    except Room.DoesNotExist:
        return render(request, "chat/error.html", {'messages' : 'this room does not exist'})
    if room is None:
        return render(request, "chat/error.html", {'messages' : 'this room does not exist'})
    info = room.info
    if pwd == 'sjsu':
        identification = judgementView(label)
        return render(request, "chat/result.html", {'info' : info, 'identification' : identification})
    else:
        return render(request, "chat/error.html", {'messages' : 'password is wrong'})



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
        'position': position,
        'messages': '',
    })
