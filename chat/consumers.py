# -*- coding: utf-8 -*-

import re
import json
import logging
import random
import time
import operator
import threading
from channels import Group
from channels import Channel
from channels.sessions import channel_session
from .models import Room
from .models import Player
import sys
reload(sys)
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
identificationDict[6] = '白狼王'
identificationDict[7] = '丘比特'
identificationDict[8] = '盗贼'



thread_pool = dict()


def keepalive(label, name, messageInfo, typo):
    message = dict()
    message['handle'] = 'keepalive'
    message['typo'] = typo
    message['message'] = messageInfo
    # try:
    #     room = Room.objects.get(label=label)
    # except Room.DoesNotExist:
    #     log.debug('ws room does not exist label=%s', label)
    #     return
    while 1:
    	try:
        	#player = room.players.filter(address=name).first()
        	Channel(name).send({'text': json.dumps(message)})
        	time.sleep(10)
        except exception:
        	break;


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
    for i in range(1, room.playerNumber + 1):
        name = room.players.filter(position=i).first().address
        Channel(name).send({'text': json.dumps(m.as_dict())})


def judgement(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1
    roleList = room.roleList.split(",")
    cunMin = int(roleList[0])
    langRen = int(roleList[1])
    if int(roleList[6]) == 1:
        langRen = langRen + 1
    shenMin = int(room.playerNumber) - cunMin - langRen
    for player in room.players.all():
        if player.identification == 8:
            log.debug('判决胜负0')
            return 0
        if player.alive == 0:
            if player.identification == 0:
                cunMin = cunMin - 1
            elif player.identification == 1 or player.identification == 6:
                langRen = langRen - 1
            else:
                shenMin = shenMin - 1
    if room.thirdteam == 1:
        count1 = 0
        count2 = 0
        for player in room.players.all():
            if player.link != -1 or player.identification == 7:
                if player.jingzhang == 1:
                    count1 = count1 + 1.5
                else:
                    count1 = count1 + 1
            else:
                if player.jingzhang == 1:
                    count2 = count2 + 1.5
                else:
                    count2 = count2 + 1
        if count1 >= count2:
            log.debug('判决胜负3')
            return 3
    if cunMin == 0 or shenMin == 0 or langRen >= (cunMin + shenMin):
        log.debug('判决胜负1')
        return 1
    elif langRen == 0:
        log.debug('判决胜负2')
        return 2
    else:
        log.debug('判决胜负0')
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
        Info = Info + '含有第三阵营！' + '\n '
    else:
        Info = Info + '不含有第三阵营！' + '\n '
    sendMessage(label, name, Info, 'message')


#发动技能，死亡结算
def skill(label, number, condition):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return 0
    player = room.players.filter(position=number).first()
    room.voteList = ''
    room.save()
    if player.jingzhang is 1:
        room.voteList = ''
        room.save()
        sendGroupMessage(label,'警长有20s时间可以传递警徽','message')
        time.sleep(20)
        jinghuiList, systemInfo = processVote(label,0)
        if len(jinghuiList) > 0:
            jiren = room.players.filter(position=int(jinghuiList)).first()
            if jiren.alive is 1:
                jiren.jingzhang = 1
                jiren.save()
                sendGroupMessage(label,jinghuiList + '号玩家成为警长','message')
        room.voteList = ''
        room.save()
        sendGroupMessage(label,str(player.position) +'号玩家有20s时间可以发动技能','message')
        time.sleep(20)
        target, systemInfo = processVote(label,0)
        if player.identification is 3 and condition == 1:
            if target is not '' and int(target) > 0:
                x = room.players.filter(position=int(target)).first()
                x.alive = 0
                x.save()
                sendGroupMessage(label,'猎人发动技能，带走' + target,'message')
                room.voteList = ''
                room.save()
                skill(label, target, 1)
        if player.link != -1:
            qinglv = room.players.filter(position=player.link).first()
            qinglv.alive = 0
            qinglv.save()
            sendGroupMessage(label,'情侣' + str(player.link) + '号玩家死亡','message')
            skill(label, player.link, -1)



def processVote(label, args):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1, 'ws room does not exist label=' + label
    count = dict()
    info = dict()
    vote = dict()
    log.debug('投票列表现在是=%s', room.voteList)
    voteList = room.voteList.split(',')
    if len(voteList) is 1:
        return '', '无人投票'
    for i in xrange(0,len(voteList),2):
        log.debug('现在i的大小是=%d', i)
        voter = voteList[i]
        # if args is not 0:
        #     if voter is not args:
        #         continue
        target = voteList[i + 1]
        log.debug('现在voter的大小是=%s', voter)
        log.debug('现在target的大小是=%s', target)
        if int(target) < 1 or int(target) > room.playerNumber:
            continue
        elif voter in vote:
            continue
        else:
            player = room.players.filter(position=voter).first()
            if player is None:
                log.debug('找不到player')
                continue
            if player.alive is 0:
                if player.identification != 3 and player.jingzhang != 1:
                    log.debug('player并没有存活')
                    continue
            vote[voter] = target
            if target in info:
                info[target] = info[target] + ',' + voter
            else:
                info[target] = '' + voter
            weight = 1
            if player.jingzhang is 1:
                weight = 1.5
            log.debug('现在的weight是：%s',weight)
            if target in count:
                count[target] = count[target] + weight
            else:
                count[target] = weight
    # deadman = max(count.iteritems(), key=operator.itemgetter(1))[0]
    deadman = ''
    currentMax = 0.0
    for key,val in count.iteritems():
        if val > currentMax:
            deadman = '' + key
            currentMax = val
        elif val == currentMax:
            deadman = deadman + ',' + key 
    systemInfo = '本轮被投的人是： ' + deadman + '\n'
    for key, val in info.iteritems():
        systemInfo = systemInfo + '投' + key + '的人有：' + val + '\n'
    return deadman, systemInfo


def processName(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return ''
    nameList = []
    if room.voteList == '':
        return nameList
    voteList = room.voteList.split(',')
    for i in xrange(0,len(voteList),2):
        if voteList[i] in nameList:
            continue
        else:
            nameList.append(voteList[i]) 
    room.voteList = ''
    room.save()
    return nameList

def checkStatus(label, nameList):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1
    log.debug('Here is the room list =%s', room.voteList)
    if len(room.voteList) is 0:
        return 0, nameList
    voteList = room.voteList.split(',')
    for i in xrange(0,len(voteList),2):
        voter = voteList[i]
        target = voteList[i + 1]
        log.debug('Here is the target :%s',target)
        if target == 'bloom':
            player = room.players.filter(position=voter).first()
            if player.identification == 1 or player.identification == 6:
                sendGroupMessage(label,'狼人' + str(voter) + '号玩家自爆！','message')
                if room.jinghui is 1:
                    sendGroupMessage(label,'昨天晚上死亡的人是'+room.deadman,'message')
                if player.identification is 6:
                    room.voteList = ''
                    room.save()
                    sendMessage(label,player.address,'你有十秒钟决定带走谁','message')
                    time.sleep(10)
                    x, y = processVote(label,0)
                    if len(x) > 0:
                        deadman = room.players.filter(position=int(x)).first()
                        deadman.alive = 0
                        deadman.save()
                        sendGroupMessage(label,'白狼王带走' + x + '号玩家！','message')
                        skill(label, int(x), 1)
                    else:
                        sendMessage(label,player.address,'你并没有发动技能！','message')
                player.alive = 0
                player.save()
                room.jinghui = 0
                room.daystatus = 0
                room.voteList = ''
                room.deadman = ''
                room.save()
                return 1, nameList
            else:
                sendMessage(label,player.address,'您不是狼人，无法自爆','message')
        elif target == 'tuishui':
            if voter in nameList:
                nameList.remove(voter)
                sendGroupMessage(label, str(voter) + '号玩家已经退水', 'message')
        elif target == 'startVote':
            room.voteList = ''
            room.save()
            return 2, nameList
    return 0, nameList

def pkStatus(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1
    voteList = room.voteList.split(',')
    log.debug('now vote list is %s',room.voteList)
    if len(room.voteList) is 0:
        return 0 
    for i in xrange(0,len(voteList),2):
        voter = voteList[i]
        target = voteList[i + 1]
        log.debug('now target is %s',target)
        if target == 'startVote':
            room.voteList = ''
            room.save()
            return 1
    return 0

def pkVote(label, nameList, count):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return [] 
    sendGroupMessage(label,'现在进入PK台，现在是第' + str(count + 1) + '轮','message')
    sendGroupMessage(label,'现在在台上的玩家是:','message')
    sendGroupMessage(label,str(nameList[0:]),'message')
    if count is 0:
        sendGroupMessage(label,'请在PK台上的人发言！','message')
    elif count is 1:
        sendGroupMessage(label,'请在PK台下的人发言！','message')
    sendGroupMessage(label,'输入startVote开始进行投票！','message')
    if count is 2:
        return []
    else:
        room.voteList = ''
        room.save()
        status = 0
        while status is 0:
            status = pkStatus(label)
            time.sleep(10)
        sendGroupMessage(label,'PK台投票开始','message')
        sendGroupMessage(label,'现在在台上的玩家是:','message')
        sendGroupMessage(label,str(nameList[0:]),'message')
        sendGroupMessage(label,'开始20s的投票','message')
        time.sleep(20)
        target, systemInfo = processVote(label,0)
        sendGroupMessage(label,systemInfo,'message')
        return target

def processLink(label):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1, 0
    voteList = room.voteList
    if len(voteList) == 0:
        number1 = random.randint(1,room.playerNumber)
        number2 = random.randint(1,room.playerNumber)
        while number2 != number1:
            number2 = random.randint(1,room.playerNumber)
        return number1, number2
    temp = voteList.split(',')
    number1 = int(temp[1])
    if len(temp) < 4:
        number2 = random.randint(1,room.playerNumber)
        while number2 != number1:
            number2 = random.randint(1,room.playerNumber)
        return number1, number2
    number2 = int(temp[3])
    return number1, number2



def room_status(label, number, gameStatus, playerList):
    try:
        room = Room.objects.get(label=label)
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return -1
    # 天黑请闭眼
    if number == 0:   
        sendGroupMessage(label, '天黑请闭眼！', 'message1')
        time.sleep(10)
        if 8 in gameStatus and room.jinghui == 1 and room.theft is -1:
            sendGroupMessage(label, '盗贼请睁眼！', 'message12')
            sendGroupMessage(label, '盗贼有两张牌可以选择,狼人牌为必选牌，请输入1和2来决定你选的牌！', 'message')
            player = room.players.filter(identification=8).first()
            if player is None:
                time.sleep(20)
            daozei = player.address 
            if playerList[len(playerList) - 1] is 1 or playerList[len(playerList) - 1] is 6:
                sendMessage(label, daozei, '你可选的牌组中有狼人牌，系统已经自动为您选择狼人牌: ' + identificationDict[playerList[len(playerList) - 1]], 'message')
                sendMessage(label, daozei, '你埋掉的牌是: ' + identificationDict[playerList[len(playerList) - 2]], 'message')
                player.identification = playerList[len(playerList) - 1]
                player.save()
                room.theft = player.position
                room.burycard = playerList[len(playerList) - 2]
                room.voteList = ''
                room.save()
                time.sleep(20)
            elif playerList[len(playerList) - 2] is 1 or playerList[len(playerList) - 2] is 6:
                sendMessage(label, daozei, '你可选的牌组中有狼人牌，系统已经自动为您选择狼人牌: ' + identificationDict[playerList[len(playerList) - 2]], 'message')
                sendMessage(label, daozei, '你埋掉的牌是: ' + identificationDict[playerList[len(playerList) - 1]], 'message')
                player.identification = playerList[len(playerList) - 2]
                player.save()
                room.theft = player.position
                room.burycard = playerList[len(playerList) - 1]
                room.voteList = ''
                room.save()
                time.sleep(20)
            else:
                card1 = identificationDict[playerList[len(playerList) - 2]]
                card2 = identificationDict[playerList[len(playerList) - 1]]
                sendMessage(label, daozei, '你可选的牌组中为: ' + card1 + ' ' + card2, 'message')
                time.sleep(10)
                cardnumber, message = processVote(label,0)
                if len(cardnumber) is 0:
                    cardnumber = random.randint(1, 2)
                if int(cardnumber) is 1:
                    sendMessage(label, daozei, '你选的牌是: ' + identificationDict[playerList[len(playerList) - 2]], 'message')
                    sendMessage(label, daozei, '你埋掉的牌是: ' + identificationDict[playerList[len(playerList) - 1]], 'message')
                    player.identification = playerList[len(playerList) - 2]
                    player.save()
                    room.theft = player.position
                    room.burycard = playerList[len(playerList) - 1]
                    room.voteList = ''
                    room.save()
                    time.sleep(10)
                else:
                    sendMessage(label, daozei, '你选的牌是: ' + identificationDict[playerList[len(playerList) - 1]], 'message')
                    sendMessage(label, daozei, '你埋掉的牌是: ' + identificationDict[playerList[len(playerList) - 2]], 'message')
                    player.identification = playerList[len(playerList) - 1]
                    player.save()
                    room.theft = player.position
                    room.burycard = playerList[len(playerList) - 2]
                    room.voteList = ''
                    room.save()
                    time.sleep(10)
            sendGroupMessage(label, '盗贼请闭眼！', 'message13')
            time.sleep(10)
        if 7 in gameStatus and room.jinghui == 1 and len(room.link) is 0:
            sendGroupMessage(label, '丘比特请睁眼！', 'message14')
            sendGroupMessage(label, '丘比特可以两次输入号码，每次请输入一个号码，这两个号码的玩家被连接为情侣！', 'message')
            player = room.players.filter(identification=7).first()
            if player is None:
                time.sleep(20)
            qiubite = player.address
            time.sleep(15)
            number1, number2 = processLink(label)
            player1 = room.players.filter(position = number1).first()
            player1.link = number2
            player1.save()
            player2 = room.players.filter(position = number2).first()
            player2.link = number1
            player2.save()
            room.link = str(number1) + ',' + str(number2)
            flag1 = player1.identification == 1 or player1.identification == 6
            flag2 = player2.identification == 1 or player2.identification == 6
            if flag1 and flag2:
                room.thirdteam = 0
            elif not flag1 and not flag2:
                room.thirdteam = 0
            else:
                room.thirdteam = 1
            room.save()
            sendMessage(label, qiubite, '您连的两个人是' + str(number1) + ' ' + str(number2), 'message')
            sendMessage(label, player1.address, '您与' + str(number2) + '号玩家被连成情侣', 'message')
            sendMessage(label, player2.address, '您与' + str(number1) + '号玩家被连成情侣', 'message')
            sendGroupMessage(label, '丘比特请闭眼！', 'message15')
            time.sleep(5)
        return 1
    # 狼人杀人
    elif number == 1:
        sendGroupMessage(label, '狼人请睁眼！', 'message3')
        if room.jinghui == 1:
            sendGroupMessage(label, '狼人请确认同伴！', 'message')
            time.sleep(10)
        time.sleep(5)
        room.voteList = ''
        room.save()
        sendGroupMessage(label, '狼人请确认击杀目标！', 'message')
        time.sleep(20)
        deadman, systemInfo = processVote(label, 0)
        if len(deadman) == 0:
            room.deadman = ''
            room.voteList = ''
            room.save()
            sendGroupMessage(label, '狼人请闭眼！', 'message4')
            time.sleep(10)
            return 2
        temp = deadman.split(',')
        if len(temp) > 1:
            deadman = 0
        else:
            deadman = int(deadman)
        room.deadman = '' + str(deadman)
        room.voteList = ''
        room.save()
        sendGroupMessage(label, '狼人请闭眼！', 'message4')
        time.sleep(10)
        return 2
    # 预言家验人
    elif number == 2:
        if 2 not in gameStatus:
            return 4
        sendGroupMessage(label, '预言家请睁眼！', 'message5')
        time.sleep(5)
        room.voteList = ''
        room.save()
        sendGroupMessage(label, '预言家请验人！', 'message')
        time.sleep(20)
        if 2 in gameStatus:
            number = 0
            # for i in range(1, room.playerNumber + 1):
            #     player = room.players.filter(position=i).first()
            #     if player.identification == 2:
            #         number = i
            #         break
            deadman, systemInfo = processVote(label,number)
            if len(deadman) is 0:
                sendGroupMessage(label, '预言家请闭眼！', 'message6')
                time.sleep(10)
                return 4
            deadman = deadman.split(',')
            if room.players.filter(position=int(deadman[0])).first().identification == 1:
                systemInfo = '您验得人是狼人！'
            else:
                systemInfo = '您验得人是好人！'
            for i in range(1, room.playerNumber + 1):
                player = room.players.filter(position=i).first()
                if player.identification == 2 and player.alive is 1:
                    sendMessage(label,player.address,systemInfo,'message')
                    break
        sendGroupMessage(label, '预言家请闭眼！', 'message6')
        time.sleep(10)
        return 4
    # 女巫救人
    elif number == 4:
        if 4 not in gameStatus:
            return 6
        sendGroupMessage(label, '女巫请睁眼！', 'message7')
        room.voteList = ''
        room.save()
        if room.jieyao is not 0:
            time.sleep(15)
            return 5
        nvwu = ''
        number = 0
        for i in range(1, room.playerNumber + 1):
            player = room.players.filter(position=i).first()
            if player.identification == 4 and player.alive is 1:
               nvwu = player.address
               number = i
               break
        if len(nvwu) > 0:
            if room.deadman == '':
                sendMessage(label,nvwu,'今天晚上无人被杀','message')
                time.sleep(5)
                return 5
            sendMessage(label,nvwu,'今天晚上被杀死的人是' + room.deadman + '号玩家，如果使用解药，请输入死者的id','message')
            player_nvwu = room.players.filter(address=nvwu).first()
            pos = 0
            if room.deadman != '':
                pos = int(room.deadman)
            if pos is player_nvwu.position and room.jinghui is 0:
                sendMessage(label,nvwu,'你无法对自己使用解药','message')
                time.sleep(5)
                return 5
            time.sleep(15)
            jieyao, systemInfo = processVote(label, 0)
            log.debug('jieyao is %s', jieyao)
            if len(jieyao) is 0:
                sendMessage(label,nvwu,'你今晚没有使用解药','message')
                time.sleep(5)
                return 5
            jieyaoList = jieyao.split(',')
            if len(jieyao) > 0:
                room.jieyao = int(jieyaoList[0])
                room.voteList = ''
                room.save()
                sendMessage(label,nvwu,'你对' + str(room.jieyao) + '号玩家使用解药','message')
                time.sleep(15)
                sendGroupMessage(label, '女巫请闭眼！', 'message8')
                time.sleep(5)
                return 6
        else:
            time.sleep(15)
            return 5
    # 女巫毒人
    elif number == 5:
        if 4 not in gameStatus:
            return 6
        room.voteList = ''
        room.save()
        if room.duyao is not 0:
            time.sleep(15)
            sendGroupMessage(label, '女巫请闭眼！', 'message8')
            time.sleep(5)
            return 6
        nvwu = ''
        number = 0
        for i in range(1, room.playerNumber + 1):
            player = room.players.filter(position=i).first()
            if player.identification == 4 and player.alive is 1:
               nvwu = player.address
               number = i
               break
        if len(nvwu) > 0:
            sendMessage(label,nvwu,'女巫可以选择使用毒药！请输入您想毒死的人的id！','message')
            time.sleep(15)
            duyao, systemInfo = processVote(label,0)
            if len(duyao) is 0:
                sendMessage(label,nvwu,'你今晚没有使用毒药','message')
                time.sleep(5)
                return 6
            duyaoList = duyao.split(',')
            if len(duyao) > 0:
                room.duyao = int(duyaoList[0])
                room.voteList = ''
                room.save()
                sendMessage(label,nvwu,'你对' + str(room.duyao) + '号玩家使用毒药','message')
                sendGroupMessage(label, '女巫请闭眼！', 'message8')
                time.sleep(5)
                return 6
        else:
            time.sleep(15)
            sendGroupMessage(label, '女巫请闭眼！', 'message8')
            time.sleep(5)
            return 6
    #守卫护人
    elif number == 6:
        if 5 not in gameStatus:
            return 7
        sendGroupMessage(label, '护卫请睁眼', 'message9')
        sendGroupMessage(label, '护卫可以选择您今晚想守卫的对象，注意两晚不能同守一个人！', 'message')
        room.voteList = ''
        room.save()
        huwei = ''
        number = 0
        for i in range(1, room.playerNumber + 1):
            player = room.players.filter(position=i).first()
            if player.identification == 5 and player.alive is 1:
               huwei = player.address
               number = i
               break
        if len(huwei) > 0:
            sendMessage(label,huwei,'请选择您今晚想守护的人！','message')
            time.sleep(20)
            huwei, systemInfo = processVote(label,0)
            if len(huwei) is 0:
                sendMessage(label,huwei,'你今晚没有守人','message')
                time.sleep(5)
                return 7
            huweiList = huwei.split(',')
            if len(huwei) > 0:
                if room.shou == int(huweiList[0]):
                    room.shou = 0
                else:
                    room.shou = int(huweiList[0])
                room.voteList = ''
                room.save()
                sendMessage(label,huwei,'你守护' + str(room.shou) + '号玩家','message')
                sendGroupMessage(label, '护卫请闭眼！', 'message10')
                time.sleep(5)
                return 7
            else:
                room.voteList = ''
                room.save()
                sendGroupMessage(label, '护卫请闭眼！', 'message10')
                time.sleep(5)
                return 7
        else:
            time.sleep(15)
            sendGroupMessage(label, '护卫请闭眼！', 'message10')
            time.sleep(5)
            return 7
    # 处理昨晚死亡数据，并调整房间状态
    elif number == 7:
        sendGroupMessage(label, '天亮了！', 'message2')
        room.daystatus = 1
        room.save()
        if room.jinghui is 1:
            room_status(label, 9, gameStatus, playerList)
        systemInfo = '昨天晚上死的人有:'
        deadList = ''
        if len(room.deadman) is 0:
            deadman = 0
        else:
            deadman = int(room.deadman)
        if deadman is not 0:
            if room.jieyao == deadman and room.shou == deadman:
                if len(deadList) is 0:
                    deadList = '' + str(deadman)
                else:
                    deadList = deadList + ',' + deadman
                player = room.players.filter(position=int(deadman)).first()
                player.alive = 0
                player.save()
                if player.link != -1:
                    qinglv = room.players.filter(position=player.link).first()
                    qinglv.alive = 0
                    qinglv.save()
                    deadList = deadList + ',' + str(player.link)
                room.save()
            elif room.jieyao == deadman or room.shou == deadman:
                room.deadman = 0
                room.save()
            else:
                if len(deadList) is 0:
                    deadList = '' + str(deadman)
                else:
                    deadList = deadList + ',' + deadman
                player = room.players.filter(position=int(deadman)).first()
                player.alive = 0
                player.save()
                if player.link != -1:
                    qinglv = room.players.filter(position=player.link).first()
                    qinglv.alive = 0
                    qinglv.save()
                    deadList = deadList + ',' + str(player.link)
                room.save()
        if room.duyao is not 0:
            player = room.players.filter(position=int(room.duyao)).first()
            if player.alive == 1:
                player.alive = 0
                player.save()
                if len(deadList) is 0:
                    deadList = '' + str(room.duyao)
                else:
                    deadList = deadList + ',' + str(room.duyao)
                if player.link != -1:
                    qinglv = room.players.filter(position=player.link).first()
                    qinglv.alive = 0
                    qinglv.save()
                    deadList = deadList + ',' + str(player.link)
        systemInfo = systemInfo + deadList
        room.deadman = deadList
        if room.jieyao is not 0:
            room.jieyao = -1
        room.save()
        sendGroupMessage(label, systemInfo, 'message')
        time.sleep(10)
        return 8
    # 死人中有猎人或者警长，可以传警徽或者发动技能
    elif number == 8:
        room.voteList = ''
        room.save()
        deadList = room.deadman
        if len(deadList) is 0:
            return 10
        else:
            temp = deadList.split(',')
            room.deadman = ''
            for i in temp:
                log.debug('here is the i number:%s',i)
                player = room.players.filter(position=int(i)).first()
                if player.jingzhang is 1:
                    room.voteList = ''
                    room.save()
                    sendGroupMessage(label,'警长有20s时间可以传递警徽','message')
                    time.sleep(20)
                    jinghuiList, systemInfo = processVote(label,0)
                    log.debug('jiren is %s', jinghuiList)
                    if len(jinghuiList) > 0:
                        jiren = room.players.filter(position=int(jinghuiList)).first()
                        if jiren.alive is 1:
                            jiren.jingzhang = 1
                            jiren.save()
                            sendGroupMessage(label,jinghuiList + '号玩家成为警长','message')
                    else:
                        sendGroupMessage(label,'警长撕掉警徽','message')
                room.voteList = ''
                room.save()
                sendGroupMessage(label,i +'玩家有20s时间可以发动技能','message')
                time.sleep(20)
                target, systemInfo = processVote(label,0)
                log.debug('target is %s', target)
                if player.identification is 3:
                    if target is not '' and int(target) > 0 and int(room.duyao) != player.position:
                        x = room.players.filter(position=int(target)).first()
                        x.alive = 0
                        x.save()
                        sendGroupMessage(label,'猎人发动技能，带走' + target,'message')
                        skill(label, target, 1)
                        room.voteList = ''
                        room.save()
            sendGroupMessage(label,'遗言阶段，如果结束遗言，可以输入startVote','message')
            yiyan = 0
            while yiyan is 0:
                yiyan, yiyan_test = checkStatus(room.label, '')
                time.sleep(10)
            return 10
    #警长竞选
    elif number== 9:
        room.voteList = ''
        room.save()
        sendGroupMessage(label,'有二十秒钟竞选警长','message')
        time.sleep(20)
        nameList = processName(label)
        if len(nameList) == 0:
            sendGroupMessage(label,'无人竞选警长，警徽流掉','message')
            room.voteList = ''
            room.jinghui = 0
            room.save()
            return 8
        sendGroupMessage(label,'参选警长的有: ' + str(nameList[0:]),'message')
        sendGroupMessage(label,'如果要开始警长投票，请输入startVote','message')
        status = 0
        while status is 0:
            status, nameList = checkStatus(label, nameList)
            time.sleep(5)
        if status is -1:
            return -1
        elif status is 1:
            return 0
        elif status is 2:
            room.voteList = ''
            room.save()
            sendGroupMessage(label,'仍然在警上的有: ' + str(nameList[0:]),'message')
            sendGroupMessage(label,'开始20s投票','message')
            time.sleep(20)
            output, systemInfo = processVote(label, 0)
            sendGroupMessage(label,systemInfo,'message')
            if len(output) is 0:
                sendGroupMessage(label,'因无人投票，警徽流掉！','message')
                return 8
            nameList = output.split(',')
            if output is not '' and len(nameList) is 1:
                room.jinghui = 0
                player = room.players.filter(position=int(nameList[0])).first()
                player.jingzhang = 1
                player.save()
                room.save()
                sendGroupMessage(label,'当选警长的人是： ' + str(nameList[0]),'message')
                return 8
            else:
                count = 0
                while len(nameList) > 1 or len(nameList) is 0:
                    nameList = pkVote(label, nameList, count)
                    count = count + 1
                if len(nameList) is 0:
                    room.jinghui = 0
                    room.save()
                else:
                    room.jinghui = 0
                    player = room.players.filter(position=int(nameList[0])).first()
                    player.jingzhang = 1
                    player.save()
                    sendGroupMessage(label,'当选警长的人是： ' + str(nameList[0]),'message')
                    room.save()
                return 8
    #发言并投票:
    elif number == 10:
        status = 0
        sendGroupMessage(label,'请进行白天的流程，输入startVote进行投票出人环节！','message')
        while status is 0:
            status, test = checkStatus(label, '')
            time.sleep(20)
        if status is -1:
            return -1
        elif status is 1:
            sendGroupMessage(label,'开始下一晚','message')
            return 0
        elif status is 2:
            room.voteList = ''
            room.save()
            sendGroupMessage(label,'开始20s投票','message')
            time.sleep(20)
            output, systemInfo = processVote(label, 0)
            sendGroupMessage(label,systemInfo,'message')
            if len(output) is 0: 
                sendGroupMessage(label,'开始下一晚' + target,'message')
                return 0
            nameList = output.split(',')
            if len(nameList) is 1:
                player = room.players.filter(position=int(nameList[0])).first()
                player.alive = 0
                player.save()
            else:
                count = 0
                while len(nameList) > 1 or len(nameList) is 0:
                    nameList = pkVote(label, nameList, count)
                    count = count + 1
                if len(nameList) is 0:
                    return 0
                else:
                    player = room.players.filter(position=int(nameList[0])).first()
                    player.alive = 0
                    player.save()
                    room.voteList = ''
                    room.save()
            room.daystatus = 0
            room.save()
            skill(label, int(nameList[0]), 1)
            sendGroupMessage(label,'遗言阶段，如果结束遗言，可以输入startVote','message')
            yiyan = 0
            while yiyan is 0:
                yiyan, yiyan_test = checkStatus(room.label, '')
                time.sleep(10)
            sendGroupMessage(label,'开始下一晚' + target,'message')
            return 0


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
    if int(roleList[2]) is not 0:
        gameStatus.append(2)
    for i in range(0, int(roleList[3])):
        playerList.append(3)
    if int(roleList[3]) is not 0:
        gameStatus.append(3)
    for i in range(0, int(roleList[4])):
        playerList.append(4)
    if int(roleList[4]) is not 0:
        gameStatus.append(4)
    for i in range(0, int(roleList[5])):
        playerList.append(5)
    if int(roleList[5]) is not 0:
        gameStatus.append(5)
    for i in range(0, int(roleList[6])):
        playerList.append(6)
    for i in range(0, int(roleList[7])):
        playerList.append(7)
    if int(roleList[7]) is not 0:
        gameStatus.append(7)
    for i in range(0, int(roleList[8])):
        playerList.append(8)
    if int(roleList[8]) is not 0:
        gameStatus.append(8)
    random.shuffle(playerList)
    if int(roleList[8]) is not 0:
        flag = True
        while flag:
            indexofplayerList = len(playerList)
            flag1 = (playerList[indexofplayerList - 1] == 1) or (playerList[indexofplayerList - 1] == 6)
            flag2 = (playerList[indexofplayerList - 2] == 1) or (playerList[indexofplayerList - 2] == 6)
            if flag1 and flag2:
                random.shuffle(playerList)
            else:
                break
    for i in range(1, room.playerNumber + 1):
        player = room.players.filter(position=i).first()
        player.identification = playerList[i - 1]
        if player.identification is 0:
            sendMessage(label,player.address,'您的身份是村民！','message')
        if player.identification is 1:
            sendMessage(label,player.address,'您的身份是狼人！','message')
        if player.identification is 2:
            sendMessage(label,player.address,'您的身份是预言家！','message')
        if player.identification is 3:
            sendMessage(label,player.address,'您的身份是猎人！','message')
        if player.identification is 4:
            sendMessage(label,player.address,'您的身份是女巫！','message')
        if player.identification is 5:
            sendMessage(label,player.address,'您的身份是守卫！','message')
        if player.identification is 6:
            sendMessage(label,player.address,'您的身份是白狼王！','message')
        if player.identification is 7:
            sendMessage(label,player.address,'您的身份是丘比特！','message')
        if player.identification is 8:
            sendMessage(label,player.address,'您的身份是盗贼！','message')
        player.save()
    sendGroupMessage(label, '身份已经准备就绪!', 'message')
    log.debug('Game Status is %s', str(gameStatus[0:]))
    roomStatus = 0
    while judgement(label) is 0:
        log.debug('房间现在的状态是%d',roomStatus)
        roomStatus = room_status(label, roomStatus, gameStatus, playerList)
        if roomStatus is -1:
            sendGroupMessage(label, '错误发生，或者测试结束！', 'message')
            break
    if judgement(label) == 1:
        sendGroupMessage(label, '狼人获胜！', 'message')
    elif judgement(label) == 2:
        sendGroupMessage(label, '好人获胜！', 'message')
    else:
        sendGroupMessage(label, '第三阵营获胜！', 'message')
    room.voteList = ''
    room.duyao = 0
    room.jieyao = 0
    room.shou = 0
    room.jinghui = 1
    room.daystatus = 0
    room.deadman = ''
    room.gameStart = 0
    room.link = ''
    room.burycard = -1
    room.theft = -1
    room.thirdteam = 0
    room.messages.all().delete()
    room.save()
    players = room.players.filter().all()
    for player in players:
        player.jingzhang = 0
        player.alive = 1
        player.identification = -1
        player.save()
    return



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
        elif data['handle'] != 0:
            room.players.create(position=data['handle'],address=message.reply_channel.name)
        log.debug('chat message room=%s handle=%s message=%s', 
            room.label, data['handle'], data['message'])
        if data['typo'] == 'startGame':
            players = room.players.all()
            room.currentNumber = len(players)
            room.save()
            if room.currentNumber < room.playerNumber:
                sendMessage(room.label, message.reply_channel.name, noEnoughPeople, 'error')
            elif room.gameStart == 1:
                sendMessage(room.label, message.reply_channel.name, gameHasStarted, 'error')
            elif room.players.all().count() < room.playerNumber:
                sendMessage(room.label, message.reply_channel.name, notReady, 'error')
            else:
                sendGroupMessage(room.label, '游戏开始!', 'message11')
                # startGame(label)
                t = threading.Thread(target=startGame, args=(label,))
                t.start()
        elif data['typo'] == 'Vote':
                sendMessage(room.label, message.reply_channel.name, voteInfo + data['message'].decode('utf8'), 'message')
                m = threading.Thread(target=keepalive, args=(label,message.reply_channel.name,'保持连接','message'))
                thread_name = str(room.label) + '-' + str(data['handle'])
                if thread_name not in thread_pool:
                    thread_pool[thread_name] = m
                    m.start()
                voteList = room.voteList
                if len(voteList) is 0:
                    room.voteList = room.voteList + data['handle'] + ',' + data['message']
                    room.save()
                else:
                    room.voteList = room.voteList + ',' + data['handle'] + ',' + data['message']
                    room.save()
        elif data['typo'] == 'bloom':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
            elif room.daystatus == 0:
                sendMessage(room.label, message.reply_channel.name, nighterror, 'error')
            else:
                if len(room.voteList) is 0:
                    room.voteList = room.voteList + data['handle'] + ',' + 'bloom'
                    room.save()
                else:
                    room.voteList = room.voteList + ',' + data['handle'] + ',' + 'bloom'
                    room.save()
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
                if player.alive is 1:
                    sendMessage(room.label, message.reply_channel.name, '您在游戏中的角色还活着，无法成为法官', 'error')
                else:
                    judgementView(room.label, message.reply_channel.name)
        elif data['typo'] == 'startVote':
            if room.gameStart == 0:
                sendMessage(room.label, message.reply_channel.name, gameNotStarted, 'error')
            else:
                if len(room.voteList) is 0:
                    room.voteList = room.voteList + data['handle'] + ',' + 'startVote'
                    room.save()
                else:
                    room.voteList = room.voteList + ',' + data['handle'] + ',' + 'startVote'
                    room.save()

                

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
            name = str(room.label) + '-' + str(player.position)
            thread_pool[name].join()
            thread_pool.pop(name)
    except (KeyError, Room.DoesNotExist):
        pass
