# -*- coding: utf-8 -*-
#!/usr/bin/python

import time
from common.basic_info import *
import sys
import asyncio
import threading
import random


class MyThread(threading.Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)


class GroupTask(object):
    def __init__(self):
        self.common = Common()

    def do_grop_work(self, grop_tasks):
        group_loop = self.common.getNewLoop()
        asyncio.set_event_loop(group_loop)
        group_result = asyncio.get_event_loop().run_until_complete(asyncio.gather(*grop_tasks, return_exceptions=False))
        return group_result

    def group_worker(self, grop_tasks):
        t = MyThread(func=self.do_grop_work, args=(grop_tasks,))
        return t

    def start_group_worker(self, threads):
        for t in threads:
            t.setDaemon(False)
            t.start()

    def join_group_worker(self, threads):
        for t in threads:
            t.join()


class Common(object):
    def __init__(self):
        pass

    def getCurrentDayTimeStampInfo(self):
        now = time.localtime()
        todayBeginTimeStr = '%d.%d.%d_00:00:00' % (now.tm_year, now.tm_mon, now.tm_mday)
        todayBeginTimeStamp = int(time.mktime(time.strptime(todayBeginTimeStr, '%Y.%m.%d_%H:%M:%S')))
        todayEndTimeStamp = todayBeginTimeStamp + 60 * 60 * 24 - 1
        return {'todayBeginTimeStamp': todayBeginTimeStamp, 'todayEndTimeStamp': todayEndTimeStamp}

    def isTimeInToday(self, checkTime):
        currentDayTimeStampInfo = self.getCurrentDayTimeStampInfo()
        todayBeginTimeStamp = currentDayTimeStampInfo['todayBeginTimeStamp']
        todayEndTimeStamp = currentDayTimeStampInfo['todayEndTimeStamp']
        checkTime = int(checkTime[:10])
        if checkTime >= todayBeginTimeStamp and checkTime < todayEndTimeStamp:
            return True
        else:
            return False

    def doDicEvaluate(self, dic, key, type=0):
        # type 表示key的类型，0表示整形（如果没找到对应的key则返回0），1表示字符串（如果没找到对应的key则返回''），2表示列表（如果没找到对应的key则返回[]），3表示返回None
        if key in dic.keys():
            return dic[key]
        else:
            if type == 0:
                return 0
            elif type == 1:
                return ''
            elif type == 2:
                return []
            elif type == 3:
                return None

    def searchDicKV(self, dic, keyword):
        if isinstance(dic, dict):
            for x in range(len(dic)):
                temp_key = list(dic.keys())[x]
                temp_value = dic[temp_key]
                if temp_key == keyword:
                    return_value = temp_value
                    return return_value
                return_value = self.searchDicKV(temp_value,keyword)
                if return_value != None:
                    return return_value

    def fixIntNum(self, num, length):
        if str(num).__len__() < length:
            num = '0' + str(num)
            self.fixIntNum(num, length)
        return num

    def isInTradeTime(self, checkTimeStamp, tradeTimeList):
        for timeDic in tradeTimeList:
            start = str(self.fixIntNum(timeDic['start'], 6))
            end = str(self.fixIntNum(timeDic['end'], 6))
            now = time.localtime()
            timeStartStr = '%d.%d.%d_%s' % (now.tm_year, now.tm_mon, now.tm_mday, start)
            timeEndStr = '%d.%d.%d_%s' % (now.tm_year, now.tm_mon, now.tm_mday, end)
            timeStartStamp = int(time.mktime(time.strptime(timeStartStr, '%Y.%m.%d_%H%M%S')))
            timeEndStamp = int(time.mktime(time.strptime(timeEndStr, '%Y.%m.%d_%H%M%S')))
            if checkTimeStamp >= timeStartStamp and checkTimeStamp < timeEndStamp:
                return True
        return False

    def getFutureLotSizeAndContractMultiplier(self, code):
        futureTypeList = allFuture.keys()
        for futureType in futureTypeList:
            if code in allFuture[futureType]['productInfo'].keys():
                lotSize = allFuture[futureType]['productInfo'][code]['lotSize']
                contractMultiplier = allFuture[futureType]['productInfo'][code]['contractMultiplier']
                return {'lotSize': lotSize, 'contractMultiplier': contractMultiplier}
        return None

    def getNewLoop(self):
        if sys.platform == 'win32':
            new_loop = asyncio.ProactorEventLoop()
        else:
            new_loop = asyncio.new_event_loop()
        return new_loop

    def randomNum(self, size=8, chars="0123456789"):
        random_num = ''.join(random.choice(chars) for _ in range(int(size)))
        return int(random_num)

if __name__ == '__main__':
    c = Common()
