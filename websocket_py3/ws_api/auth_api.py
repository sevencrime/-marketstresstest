# -*- coding: utf-8 -*-
# !/usr/bin/python

import time
from google.protobuf import json_format
from pb_files.auth_pb2 import *
from test_config import *
from websocket_py3.ws_base.ws_client import *
from common.common_method import Common
import json


class AuthApi(object):
    def __init__(self, ws_url, new_loop, extra_headers=None):
        self.new_loop = new_loop
        self.client = BaseWebSocketClient(url=ws_url, loop=self.new_loop, extra_headers=extra_headers)
        self.common = Common()

    async def AuthReqApi(self, token):
        msg_id = self.common.randomNum(10)
        data_send = AuthReq(token=token)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.AUTH_CENTER_AUTH, data=data_send.SerializeToString(), id=msg_id, version=ProtoVersion.VERSION_1)
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg, recv_num=1)
        json_rsp_list = []
        for base_req in all_req:
            if base_req == None:
                continue
            if base_req == '_Heart_PONG':
                base_req = await self.client.recv()
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.AUTH_CENTER_AUTH:
                single_data = AuthRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
        # print('AuthReqApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    async def HearBeatApi(self):
        await self.client.send('_Heart_PING')


if __name__ == '__main__':
    common = Common()
    api = AuthApi(auth_ws_url, asyncio.get_event_loop(), extra_headers=auth_headers)
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(api.client.ws_connect())
    asyncio.get_event_loop().run_until_complete(api.AuthReqApi(token=str(market_token)))
    asyncio.get_event_loop().run_until_complete(api.client.stress_disconnect())


