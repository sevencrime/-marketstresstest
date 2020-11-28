# -*- coding: utf-8 -*-
# !/usr/bin/python

import websockets
import asyncio
import sys
import time


class BaseWebSocketClient(object):
    def __init__(self, url, loop=None, close_timeout=1, timeout=120, extra_headers=None):
        self.url = url
        self.loop = loop
        self.close_timeout = close_timeout
        self.timeout = timeout
        self.extra_headers = extra_headers

    async def ws_connect(self):
        try:
            asyncio.set_event_loop(self.loop)
            self._ws = await websockets.connect(self.url, close_timeout=self.close_timeout, timeout=self.timeout, extra_headers=self.extra_headers)
        except Exception as e:
            print('Connect Error:', e)
            assert False

    async def send(self, send_content):
        try:
            await self._ws.send(send_content)
        except Exception as e:
            print('Ws client send error, please check!\n', e)

    async def recvSingle(self, index):
        rsp = None
        try:
            rsp = await self._ws.recv()
        except asyncio.CancelledError:
            print('ws recv timeout to skip!')
        except Exception as e:
            print('Ws client recvSingle error, please check!\n', e)
        finally:
            return rsp

    async def recv(self, recv_num=1, recv_timeout_sec=24):
        rspList = []
        try:
            for i in range(recv_num):
                task = {asyncio.ensure_future(self.recvSingle(i))}
                doneSet, pendingSet = await asyncio.wait(task, timeout=recv_timeout_sec)
                for doneInfo in doneSet:
                    if doneInfo._result != None: # 因断连等原因导致返回为None时，这里过滤掉
                        rspList.append(doneInfo._result)
                if pendingSet:
                    for pending in pendingSet:
                        pending.cancel()
                    break
        except BaseException as e:
            print('Ws client recv error, please check!\n', e)
        return rspList

    async def send_and_recv(self, send_content, recv_num=1):
        await self.send(send_content)
        rspList = await self.recv(recv_num=recv_num)
        return rspList

    def disconnect(self):
        try:
            asyncio.set_event_loop(self.loop)
            asyncio.get_event_loop().run_until_complete(self._ws.close())
        except Exception as e:
            print('disconnect ws error:\n', e)

    async def stress_disconnect(self):
        try:
            await self._ws.close()
        except Exception as e:
            print('disconnect ws error:\n', e)

    def is_disconnect(self):
        '''
        CONNECTING, OPEN, CLOSING, CLOSED = range(4)
        '''
        if self._ws.state == 1:
            return False
        elif self._ws.state in (2, 3):
            return True

if __name__ =='__main__':
    start = time.time()
    ipAddress = 'ws://127.0.0.1'
    port = 10080
    url = ipAddress + ':' + str(port)
    # task_num = 5000
    # async def do_single_work(x):
    #     if sys.platform == 'win32':
    #         new_loop = asyncio.ProactorEventLoop()
    #     else:
    #         new_loop = asyncio.new_event_loop()
    #     client = BaseWebSocketClient(url, new_loop)
    #     await client.ws_connect()
    #     await client.send_and_recv(str(x),recv_num=1)
    #     await client.disconnect()
    # tasks = [do_single_work(i+1) for i in range(task_num)]
    # if sys.platform == 'win32':
    #     new_loop = asyncio.ProactorEventLoop()
    # else:
    #     new_loop = asyncio.new_event_loop()
    #
    # asyncio.set_event_loop(new_loop)
    # asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
    # # asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    # end = time.time()
    # print(end-start)

    if sys.platform == 'win32':
        new_loop = asyncio.ProactorEventLoop()
    else:
        new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    client = BaseWebSocketClient(url, new_loop)
    asyncio.get_event_loop().run_until_complete(client.ws_connect())
    asyncio.get_event_loop().run_until_complete(client.send('11111111'))
    asyncio.get_event_loop().run_until_complete(client.send('222222222'))

    print((client.is_disconnect()))
    asyncio.get_event_loop().run_until_complete(client.disconnect())

    print(client.is_disconnect())

