#coding=utf-8

import re
import json
import logging
import random
import time
import operator
import sys
from channels import Group
from channels import Channel
from channels.sessions import channel_session
from .models import Room
from .models import Player

sys.setdefaultencoding("utf-8")

log = logging.getLogger(__name__)


noEnoughPeople = '房间人数不足'
gameHasStarted = '游戏已经开始'
gameNotStarted = '游戏尚未开始'
notReady = '有人没准备好'
notRightPerson = '您本轮无法投票'
voteInfo = '您投票给 '
dayerror = '时间是白天'
nighterror = '时间是夜晚'
identification = '您的身份是 '

identificationDict = dict()
identificationDict[0] = '村民'
identificationDict[1] = '狼人'
identificationDict[2] = '预言家'
identificationDict[3] = '女巫'
identificationDict[4] = '猎人'
identificationDict[5] = '守卫'

def sendMessage(label, name, messageInfo, typo):
    message = dict()
    message['handle'] = '系统信息'
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
    message['handle'] = '系统信息'
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
        return 0

def judgementView(label, name):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        sendMessage(label, name, '房间不存在!', 'error')
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
    if len(shouwei) > 0:
        Info = Info + '守卫: ' + shouwei + '\n '
    sendMessage(label, name, Info, 'message')


def processVote(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1, 'ws room does not exist label=' + label
    count = dict()
    info = dict()
    vote = dict()
    voteList = room.voteList.split(',')
    for i in xrange(0,len(voteList),2):
        voter = voteList[i]
        target = voteList[i + 1]
        if int(target) < 1 or int(target) > room.playerNumber:
            continue
        elif voter in vote:
            continue
        else:
            if room.players.filter(position=voter).alive is 0:
                continue
            vote[voter] = target
            if target not in info:
                info[target] = info[target] + ',' + voter
            else:
                info[target] = '' + voter
            weight = 1
            if room.players.filter(position=voter).jingzhang is 1:
                weight = 1.5
            if target in count:
                count[target] = count[target] + weight
            else:
                count[target] = weight
    deadman = max(count.iteritems(), key=operator.itemgetter(1))[0]
    systemInfo = '本轮被投的人是： ' + deadman + '\n'
    for key, val in info.iteritems():
        systemInfo = systemInfo + '投' + key + '的人有：' + val + '\n'
    return deadman, systemInfo










def room_status(label, number, gameStatus):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -2
    if number == 1:
        sendGroupMessage(label, '天黑请闭眼！', 'message')
        return 2
    elif number == 2:
        time.sleep(10)
        sendGroupMessage(label, '狼人请睁眼！', 'message')
        if room.jinghui == 1:
            sendGroupMessage(label, '狼人请确认同伴！', 'message')
            time.sleep(10)
        time.sleep(5)
        room.voteList = ''
        room.save()
        sendGroupMessage(label, '狼人请确认击杀目标！', 'message')
        time.sleep(30)
        deadman, systemInfo = processVote(label)
        room.deadman = deadman
        room.voteList = ''
        room.save()
        sendGroupMessage(label, '狼人请闭眼！', 'message')
        time.sleep(10)
    elif number == 3:
        time.sleep(10)
        sendGroupMessage(label, '预言家请睁眼！', 'message')
        time.sleep(5)
        room.voteList = ''
        room.save()
        sendGroupMessage(label, '预言家请验人！', 'message')
        time.sleep(30)
        if 2 in gameStatus:
            deadman, systemInfo = processVote(label)
            if room.players.filter(position=deadman).identification == 1:
                systemInfo = '您验得人是狼人！'
            else:
                systemInfo = '您验得人是好人！'
            for i in range(1, room.playerNumber + 1):
                player = room.players.filter(position=i).first()
                if player.identification == 2:
                    sendMessage(label,player.address,systemInfo,'message')
    elif number == 4:
        return -1



def startGame(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        sendGroupMessage(label, 'room does not exist!', 'error')
        return
    room.gameStart = 1
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
    sendGroupMessage(label, '身份已经准备就绪!', 'message')
    status = 0
    while judgement(label) != 0:
        status = room_status(label, status, gameStatus)
    if judgement(label) == 1:
        sendGroupMessage(label, '狼人获胜！', 'message')
    else:
        sendGroupMessage(label, '好人获胜！', 'message')












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
        log.debug('游戏开始!')
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
            elif room.dayStatus == 0:
                sendMessage(room.label, message.reply_channel.name, nighterror, 'error')
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
                player = room.players.filter(position=data['handle']).first
                if player.alive is 1:
                    sendMessage(room.label, message.reply_channel.name, '您在游戏中的角色还活着，无法成为法官', 'error')
                else:
                    judgementView(room.label, message.reply_channel.name)

                





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
