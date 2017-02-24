#coding=utf-8

import re
import json
import logging
import random
from channels import Group
from channels import Channel
from channels.sessions import channel_session
from .models import Room
from .models import Player


log = logging.getLogger(__name__)


noEnoughPeople = 'not enough people in the room'
gameHasStarted = 'game has started'
gameNotStarted = 'game does not start'
notReady = 'someone is not ready'
notRightPerson = 'You are not the right person to vote'
voteInfo = 'You vote '
dayerror = 'This is in the day'
nighterror = 'This is in the night'
identification = 'Your identification is '

identificationDict = dict()
identificationDict[0] = 'cunmin'
identificationDict[1] = 'langren'
identificationDict[2] = 'yuyanjia'
identificationDict[3] = 'nvwu'
identificationDict[4] = 'lieren'
identificationDict[5] = 'shouwei'

def sendMessage(label, name, messageInfo, typo):
    message = dict()
    message['handle'] = 'system'
    message['typo'] = typo
    message['message'] = messageInfo
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return
    m = room.messages.create(**message)
    Channel(name).send({'text': json.dumps(m.as_dict())})

def sendGroupMessage(label, messageInfo, typo):
    message = dict()
    message['handle'] = 'system'
    message['typo'] = typo
    message['message'] = messageInfo
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return
    m = room.messages.create(**message)
    Group('chat-'+label).send({'text': json.dumps(m.as_dict())})


def judgement(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1
    roleList = room.roleList.split(",")
    cunMin = roleList[0]
    langRen = roleList[1]
    shenMin = room.playerNumber - cunMin - langRen
    for player in room.players.all():
        if player.alive == 0:
            if player.identification == 0:
                cunMin = cunMin - 1
            elif player.identification == 1:
                langRen = langRen - 1
            else:
                shenMin = shenMin - 1
    if cunMin == 0 or shenMin == 0 or langRen >= cunMin + shenMin:
        return 1
    elif langRen == 0:
        return 2
    else:
        return 3

def judgementView(label, name):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        sendMessage(label, name, 'room does not exist!', 'error')
        return
    cunmin = ''
    langren = ''
    yuyanjia = ''
    nvwu = ''
    shouwei = ''
    lieren = ''
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
    Info = 'Identification list \ '
    if cunmin.len() > 0:
        Info = Info + 'cunmin: ' + cunmin + '\ '
    if langren.len() > 0:
        Info = Info + 'langren: ' + langren + '\ '
    if yuyanjia.len() > 0:
        Info = Info + 'yuyanjia: ' + yuyanjia + '\ '
    if lieren.len() > 0:
        Info = Info + 'lieren: ' + lieren + '\ '
    if nvwu.len() > 0:
        Info = Info + 'nvwu: ' + nvwu + '\ '
    if shouwei.len() > 0:
        Info = Info + 'shouwei: ' + shouwei + '\ '
    sendMessage(label, name, Info, 'message')




def room_status(label, number, gameStatus):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -2

def startGame(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        sendGroupMessage(label, 'room does not exist!', 'error')
        return
    room.gameStatus = 1
    room.save()
    roleList = room.roleList.split(",")
    playerList = []
    gameStatus = []
    gameStatus.append(0)
    gameStatus.append(1)
    for i in range(0, int(roleList[0])):
        playerList.append(0)
    for i in range(0, int(roleList[1])):
        playerList.append(1)
    for i in range(0, int(roleList[2])):
        playerList.append(2)
    if roleList[2] is not 0:
        gameStatus.append(2)
    for i in range(0, int(roleList[3])):
        playerList.append(3)
    if roleList[3] is not 0:
        gameStatus.append(3)
    for i in range(0, int(roleList[4])):
        playerList.append(4)
    if roleList[4] is not 0:
        gameStatus.append(4)
    for i in range(0, int(roleList[5])):
        playerList.append(5)
    if roleList[5] is not 0:
        gameStatus.append(5)
    random.shuffle(playerList)
    for i in range(1, room.playerNumber + 1):
        player = room.players.filter(position=i).first()
        player.identification = playerList[i - 1]
        player.save()
    sendGroupMessage(label, 'identification is ready!', 'message')












@channel_session
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)

    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s', 
        room.label, message['client'][0], message['client'][1])

    if room.playerNumber == room.currentNumber:
        log.debug('room is full')
        return
    if room.gameStart == 1:
        log.debug('game has been started!')
        return
    # Need to be explicit about the channel layer so that testability works
    # This may be a FIXME?
    Room.objects.filter(label=label).update(currentNumber=room.currentNumber + 1)
    Group('chat-'+label).add(message.reply_channel)
    message.channel_session['room'] = room.label

@channel_session
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return


    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return
    
    if set(data.keys()) != set(('handle', 'message', 'typo')):
        log.debug("ws message unexpected format data=%s", data)
        return

    if data:
        player = None
        try:
            player = room.players.filter(position=data['handle']).first()
        except ValueError:
            log.debug("something is wrong")
        if player is not None:
            if player.address != message.reply_channel.name:
                log.debug("this room's position has been occupied by another guy")
                sendMessage(room.label, message.reply_channel.name, "this room's position has been occupied by another guy", 'error')
        else:
            room.players.create(position=data['handle'],address=message.reply_channel.name)
        log.debug('chat message room=%s handle=%s message=%s', 
            room.label, data['handle'], data['message'])
        if data['typo'] == 'startGame':
            if room.currentNumber < room.playerNumber:
                sendMessage(room.label, message.reply_channel.name, noEnoughPeople, 'error')
            elif room.gameStart == 1:
                sendMessage(room.label, message.reply_channel.name, gameHasStarted, 'error')
            elif room.players.all().count() < room.playerNumber:
                sendMessage(room.label, message.reply_channel.name, notReady, 'error')
            else:
                sendGroupMessage(room.label, 'Game Starts!', 'message')
                startGame(label)
        elif data['typo'] == 'Vote':
                sendMessage(room.label, message.reply_channel.name, voteInfo + data['message'], 'message')
        elif data['typo'] == 'posion':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
        elif data['typo'] == 'heal':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
        elif data['typo'] == 'bloom':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
        elif data['typo'] == 'identification':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
            else:
                player = room.players.filter(position=data['handle']).first()
                sendMessage(room.label, message.reply_channel.name, identification + identificationDict[player.identification], 'message')
        elif data['typo'] == 'judgement':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
            else:
                player = room.players.filter(position=data['handle']).first()
                judgementView(label, player.address)
                





        #m = room.messages.create(**data)

        # See above for the note about Group
        #Group('chat-'+label).send({'text': json.dumps(m.as_dict())})

@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        Group('chat-'+label).discard(message.reply_channel)
        player = room.players.filter(address=message.reply_channel.name).first()
        if player is not None:
            Room.objects.filter(label=label).update(currentNumber=room.currentNumber - 1)
            room.players.filter(address=message.reply_channel.name).delete()
    except (KeyError, Room.DoesNotExist):
        pass
