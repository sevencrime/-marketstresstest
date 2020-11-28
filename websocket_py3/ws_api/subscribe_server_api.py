# -*- coding: utf-8 -*-
#!/usr/bin/python

import time

from google.protobuf import json_format

from pb_files.common_msg_def_pb2 import *
from pb_files.quote_msg_def_pb2 import *
from pb_files.quote_type_def_pb2 import *
from test_config import *
from websocket_py3.ws_base.ws_client import *
from common.common_method import Common
import json


class SubscribeApi(object):
    def __init__(self, ws_url, new_loop):
        self.new_loop = new_loop
        self.client = BaseWebSocketClient(url=ws_url, loop=self.new_loop)
        self.common = Common()

    # 登录请求
    async def LoginReq(self, token, start_time_stamp=None):
        data_send = LoginReq(auto_token=token, start_time_stamp=start_time_stamp)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.LOGIN_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg)
        json_login_list = []
        for req in all_req:
            recv_data = QuoteMsgCarrier()
            recv_data.ParseFromString(req)
            if recv_data.type == QuoteMsgType.LOGIN_RSP:
                login_data = LoginRsp()
                login_data.ParseFromString(recv_data.data)
                json_login_data = json_format.MessageToJson(login_data)
                json_login_data = json.loads(json_login_data)
                json_login_list.append(json_login_data)
        # print(json_login_list)
        return json_login_list

    # 登出请求
    async def LogoutReq(self, start_time_stamp=None, recv_num=1):
        data_send = LoginReq(start_time_stamp=start_time_stamp)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.LOGOUT_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg, recv_num=recv_num)
        json_logout_list = []
        for req in all_req:
            recv_data = QuoteMsgCarrier()
            recv_data.ParseFromString(req)
            if recv_data.type == QuoteMsgType.LOGOUT_RSP:
                login_data = LogoutRsp()
                login_data.ParseFromString(recv_data.data)
                json_logout_data = json_format.MessageToJson(login_data)
                json_logout_data = json.loads(json_logout_data)
                json_logout_list.append(json_logout_data)
        print('LogoutReq json_logout_list:{}'.format(json_logout_list))
        return json_logout_list

    # 心跳
    async def HearbeatReqApi(self, connid, isKeep=False):
        data_send = HeartReqMsg(conn_id=connid)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.HEARTBEAT_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        if isKeep == False:
            all_req = await self.client.send_and_recv(quote_msg)
            json_rsp_list = []
            for base_req in all_req:
                if base_req == None:
                    continue
                rev_data = QuoteMsgCarrier()
                rev_data.ParseFromString(base_req)
                if rev_data.type == QuoteMsgType.HEARTBEAT_RSP:
                    single_data = HeartRspMsg()
                    single_data.ParseFromString(rev_data.data)
                    json_single_data = json_format.MessageToJson(single_data)
                    json_single_data = json.loads(json_single_data)
                    json_rsp_list.append(json_single_data)
            # print('HearbeatReqApi json_rsp_list:{}'.format(json_rsp_list))
            return json_rsp_list
        else:
            await self.client.send(quote_msg)

    # 保持心跳
    async def hearbeat_job(self, gap_time=1):
        i = 1
        asyncio.set_event_loop(self.new_loop)
        while True:
            if self.client.is_disconnect():
                break
            await self.HearbeatReqApi(connid=i, isKeep=True)
            # print('The {} time to keep heartbeat! SendTimeStamp:{}'.format(i, str(time.time())))
            await asyncio.sleep(gap_time)
            i = i + 1

    # 测速
    async def VelocityReqApi(self, start_time=None):
        data_send = VelocityReqMsg(start_time=start_time)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.VELOCITY_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.VELOCITY_RSP:
                single_data = VelocityRspMsg()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
        # print('VelocityReqApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 订阅
    async def SubsQutoMsgReqApi(self, sub_type=None, child_type=None, base_info=None, recv_num=1, start_time_stamp=None, sub_quote_type=SubQuoteMsgType.REAL_QUOTE_MSG):
        # Return:
        # {
        #     'first_rsp_list': [{}, {}, {}],  # 表示订阅应答响应 SUBSCRIBE_RSP
        #     'snapshot_json_list': [{}, {}, {}, {}, {}],  # 表示返回的当前时间之前的合约快照数据
        #     'basic_json_list': [{}, {}, {}, {}, {}]  # 表示返回的当前时间之前的合约静态数据
        # }
        # print('''sub_type:{}, child_type:{}, base_info:{}'''.format(sub_type, child_type, base_info))
        send_data = SubscribeQuoteMsgReq(sub_type=sub_type, child_type=child_type, base_info=base_info, start_time_stamp=start_time_stamp, sub_quote_type=sub_quote_type)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.SUBSCRIBE_REQ, data=send_data.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        await self.HearbeatReqApi(connid=10086, isKeep=True)  # 避免循环接消息时心跳断掉
        all_req = await self.client.send_and_recv(quote_msg, recv_num=recv_num)
        first_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.SUBSCRIBE_RSP:
                single_data = SubscribeQuoteMsgRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                first_rsp_list.append(json_single_data)

            elif rev_data.type == QuoteMsgType.HEARTBEAT_RSP:  # 如果接到心跳数据应忽略,继续接受一次
                all_req = await self.client.recv(recv_num=1)
                for base_req in all_req:
                    rev_data = QuoteMsgCarrier()
                    rev_data.ParseFromString(base_req)
                    if rev_data.type == QuoteMsgType.SUBSCRIBE_RSP:
                        single_data = SubscribeQuoteMsgRsp()
                        single_data.ParseFromString(rev_data.data)
                        json_single_data = json_format.MessageToJson(single_data)
                        json_single_data = json.loads(json_single_data)
                        first_rsp_list.append(json_single_data)
        finally_rsp = {}
        finally_rsp['first_rsp_list'] = first_rsp_list
        before_snapshot_json_list = []
        before_basic_json_list = []
        # 接收该合约前一刻的最新一笔静态、快照，直到更新时间超出请求时间则跳出
        # while True:
        #     before_time_reqs = await self.client.recv(recv_num=1)
        #     if before_time_reqs != []:
        #         base_req = before_time_reqs[0]
        #         rev_data = QuoteMsgCarrier()
        #         rev_data.ParseFromString(base_req)
        #         if rev_data.type == QuoteMsgType.PUSH_SNAPSHOT:
        #             single_data = QuoteSnapshot()
        #             single_data.ParseFromString(rev_data.data)
        #             json_snapshot_data = json_format.MessageToJson(single_data)
        #             json_snapshot_data = json.loads(json_snapshot_data)
        #             # print('before_json_snapshot_data:{}'.format(json_snapshot_data))
        #             req_source_time = self.common.searchDicKV(json_snapshot_data, 'sourceUpdateTime')
        #             instr_code = self.common.searchDicKV(json_snapshot_data, 'instrCode')
        #             # 毫秒级别对比
        #             if int(int(req_source_time) / (pow(10, 6))) < start_time_stamp:
        #                 before_snapshot_json_list.append(json_snapshot_data)
        #                 # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_snapshot_data)
        #             else:
        #                 break
        #         elif rev_data.type == QuoteMsgType.PUSH_BASIC:
        #             single_data = QuoteBasicInfo()
        #             single_data.ParseFromString(rev_data.data)
        #             basic_single_data = json_format.MessageToJson(single_data)
        #             basic_single_data = json.loads(basic_single_data)
        #             # print('before_basic_single_data:{}'.format(basic_single_data))
        #             req_source_time = self.common.searchDicKV(basic_single_data, 'updateTimestamp')
        #             instr_code = self.common.searchDicKV(basic_single_data, 'instrCode')
        #             # 毫秒级别对比
        #             if int(int(req_source_time) / (pow(10, 6))) < start_time_stamp:
        #                 before_basic_json_list.append(basic_single_data)
        #                 # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, basic_single_data)
        #             else:
        #                 break
        #         elif rev_data.type not in [QuoteMsgType.PUSH_SNAPSHOT, QuoteMsgType.PUSH_BASIC, QuoteMsgType.HEARTBEAT_RSP, QuoteMsgType.SUBSCRIBE_RSP]:
        #             break
        #     else:
        #         break
        finally_rsp['before_snapshot_json_list'] = before_snapshot_json_list
        finally_rsp['before_basic_json_list'] = before_basic_json_list
        return finally_rsp

    # 取消行情订阅
    async def UnSubsQutoMsgReqApi(self, unsub_type, unchild_type=None, unbase_info=None, recv_num=20, start_time_stamp=None):
        # print('''sub_type:{}, child_type:{}, base_info:{}'''.format(unsub_type, unchild_type, unbase_info))
        send_data = UnsubscribeQuoteMsgReq(sub_type=unsub_type, child_type=unchild_type, base_info=unbase_info,
                                         stat_time_stamp=start_time_stamp)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.UNSUBSCRIBE_REQ, data=send_data.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg, recv_num=recv_num)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.UNSUBSCRIBE_RSP:
                single_data = UnsubscribeQuoteMsgRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
        # print('UnSubsQutoMsgReqApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 订阅盘口数据（依赖订阅接口）
    async def QuoteOrderBookDataApi(self, recv_num=10, is_filter=True):
        await self.HearbeatReqApi(connid=10086, isKeep=True)   # 避免循环接消息时心跳断掉
        all_req = await self.client.recv(recv_num)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if is_filter:
                if rev_data.type == QuoteMsgType.PUSH_ORDER_BOOK:
                    single_data = QuoteOrderBookData()
                    single_data.ParseFromString(rev_data.data)
                    json_single_data = json_format.MessageToJson(single_data)
                    json_single_data = json.loads(json_single_data)
                    json_rsp_list.append(json_single_data)
                    req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                    instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                    # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)

            else:
                single_data = QuoteOrderBookData()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
        # print('QuoteOrderBookDataApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 订阅逐笔成交数据（依赖订阅接口）
    async def QuoteTradeDataApi(self, recv_num=10, is_filter=True):
        all_req = await self.client.recv(recv_num)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if is_filter:
                if rev_data.type == QuoteMsgType.PUSH_TRADE_DATA:
                    single_data = QuoteTradeData()
                    single_data.ParseFromString(rev_data.data)
                    json_single_data = json_format.MessageToJson(single_data)
                    json_single_data = json.loads(json_single_data)
                    json_rsp_list.append(json_single_data)
                    req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                    instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                    # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
            else:
                single_data = QuoteTradeData()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
        # print('QuoteTradeDataApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 订阅静态数据（依赖订阅接口）
    async def QuoteBasicInfoApi(self, recv_num=10, is_filter=True):
        all_req = await self.client.recv(recv_num)
        json_basic_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if is_filter:
                if rev_data.type == QuoteMsgType.PUSH_BASIC:
                    basic_data = QuoteBasicInfo()
                    basic_data.ParseFromString(rev_data.data)
                    json_basic_data = json_format.MessageToJson(basic_data)
                    json_basic_data = json.loads(json_basic_data)
                    json_basic_list.append(json_basic_data)
                    req_source_time = self.common.searchDicKV(json_basic_data, 'sourceUpdateTime')
                    instr_code = self.common.searchDicKV(json_basic_data, 'instrCode')
                    # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_basic_data)
            else:
                basic_data = QuoteTradeData()
                basic_data.ParseFromString(rev_data.data)
                json_basic_data = json_format.MessageToJson(basic_data)
                json_basic_data = json.loads(json_basic_data)
                json_basic_list.append(json_basic_data)
                req_source_time = self.common.searchDicKV(json_basic_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_basic_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_basic_data)
        # print('QuoteBasicInfoApi json_rsp_list:{}'.format(json_basic_list))
        return json_basic_list

    # 订阅快照数据（依赖订阅接口）
    async def QuoteSnapshotApi(self, recv_num=10, is_filter=True):
        if self.client.is_disconnect():
            return []
        await self.HearbeatReqApi(connid=10086, isKeep=True)   # 避免循环接消息时心跳断掉
        all_req = await self.client.recv(recv_num)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if is_filter:
                if rev_data.type == QuoteMsgType.PUSH_SNAPSHOT:
                    basic_data = QuoteSnapshot()
                    basic_data.ParseFromString(rev_data.data)
                    json_basic_data = json_format.MessageToJson(basic_data)
                    json_basic_data = json.loads(json_basic_data)
                    json_rsp_list.append(json_basic_data)
                    req_source_time = self.common.searchDicKV(json_basic_data, 'sourceUpdateTime')
                    instr_code = self.common.searchDicKV(json_basic_data, 'instrCode')
                    # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_basic_data)
            else:
                basic_data = QuoteSnapshot()
                basic_data.ParseFromString(rev_data.data)
                json_basic_data = json_format.MessageToJson(basic_data)
                json_basic_data = json.loads(json_basic_data)
                json_rsp_list.append(json_basic_data)
                req_source_time = self.common.searchDicKV(json_basic_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_basic_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_basic_data)
        # print('QuoteSnapshotApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 手机Api---开始请求分时页面数据
    async def StartChartDataReqApi(self, exchange, code, frequency, start_time,start_time_stamp):
        data_send = StartChartDataReq(exchange=exchange, code=code, frequency=frequency, start_time=start_time, start_time_stamp=start_time_stamp)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.START_CHART_DATA_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg)
        first_app_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.START_CHART_DATA_RSP:
                single_data = StartChartDataRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                first_app_rsp_list.append(json_single_data)
        # print('StartChartDataReqApi first_rsp_list:{}'.format(first_app_rsp_list))
        finally_rsp = {}
        finally_rsp['first_app_rsp_list'] = first_app_rsp_list
        before_appsnapshot_json_list = []
        before_appbasic_json_list = []
        # 接收该app订阅前一刻的最新一笔静态、快照，直到更新时间超出请求时间则跳出
        while True:
            before_time_reqs = await self.client.recv(recv_num=1)
            if before_time_reqs != []:
                for base_req in before_time_reqs:
                    rev_data = QuoteMsgCarrier()
                    rev_data.ParseFromString(base_req)
                    if rev_data.type == QuoteMsgType.PUSH_SNAPSHOT:
                        single_data = QuoteSnapshot()
                        single_data.ParseFromString(rev_data.data)
                        json_snapshot_data = json_format.MessageToJson(single_data)
                        json_snapshot_data = json.loads(json_snapshot_data)
                        req_source_time = self.common.searchDicKV(json_snapshot_data, 'sourceUpdateTime')
                        instr_code = self.common.searchDicKV(json_snapshot_data, 'instrCode')
                        # 毫秒级别对比
                        if int(req_source_time / (pow(10, 6))) < start_time_stamp:
                            before_appsnapshot_json_list.append(json_snapshot_data)
                            # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_snapshot_data)
                        else:
                            break
                    elif rev_data.type == QuoteMsgType.PUSH_BASIC:
                        single_data = QuoteBasicInfo()
                        single_data.ParseFromString(rev_data.data)
                        basic_single_data = json_format.MessageToJson(single_data)
                        basic_single_data = json.loads(basic_single_data)
                        req_source_time = self.common.searchDicKV(basic_single_data, 'sourceUpdateTime')
                        instr_code = self.common.searchDicKV(basic_single_data, 'instrCode')
                        # 毫秒级别对比
                        if int(req_source_time / (pow(10, 6))) < start_time_stamp:
                            before_appbasic_json_list.append(basic_single_data)
                            # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, basic_single_data)
                        else:
                            break
                    else:
                        break
            else:
                break
        finally_rsp['before_appsnapshot_json_list'] = before_appsnapshot_json_list
        finally_rsp['before_appbasic_json_list'] = before_appbasic_json_list
        # print('StartChartDataReqApi finally_rsp:{}'.format(finally_rsp))
        return finally_rsp

    # 手机Api---结束请求分时页面数据
    async def StopChartDataReqApi(self, exchange, code,start_time_stamp):
        data_send = StopChartDataReq(exchange=exchange, code=code, start_time_stamp=start_time_stamp)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.STOP_CHART_DATA_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.STOP_CHART_DATA_RSP:
                single_data = StopChartDataRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
        # print('StopChartDataReqApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 手机Api---推送分时数据
    async def PushKLineMinDataApi(self, recv_num=10, is_filter=True):
        all_req = await self.client.recv(recv_num)
        json_basic_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if is_filter:
                if rev_data.type == QuoteMsgType.PUSH_KLINE_MIN:
                    basic_data = PushKLineMinData()
                    basic_data.ParseFromString(rev_data.data)
                    json_basic_data = json_format.MessageToJson(basic_data)
                    json_basic_data = json.loads(json_basic_data)
                    json_basic_list.append(json_basic_data)
                    req_source_time = self.common.searchDicKV(json_basic_data, 'sourceUpdateTime')
                    instr_code = self.common.searchDicKV(json_basic_data, 'code')
                    # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_basic_data)
            else:
                basic_data = PushKLineMinData()
                basic_data.ParseFromString(rev_data.data)
                json_basic_data = json_format.MessageToJson(basic_data)
                json_basic_data = json.loads(json_basic_data)
                json_basic_list.append(json_basic_data)
                req_source_time = self.common.searchDicKV(json_basic_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_basic_data, 'code')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_basic_data)
        # print('PushKLineMinDataApi json_rsp_list:{}'.format(json_basic_list))
        return json_basic_list

    # 手机Api---请求分时页面数据，会主推静态、快照、盘口、逐笔、分时数据，此方法用于接收
    async def AppQuoteAllApi(self, recv_num=20):
        all_req = await self.client.recv(recv_num)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.PUSH_BASIC:
                single_data = QuoteBasicInfo()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
            elif rev_data.type == QuoteMsgType.PUSH_SNAPSHOT:
                single_data = QuoteSnapshot()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
            elif rev_data.type == QuoteMsgType.PUSH_ORDER_BOOK:
                single_data = QuoteOrderBookData()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
            elif rev_data.type == QuoteMsgType.PUSH_TRADE_DATA:
                single_data = QuoteTradeData()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'instrCode')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
            elif rev_data.type == QuoteMsgType.PUSH_KLINE_MIN:
                single_data = PushKLineMinData()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
                req_source_time = self.common.searchDicKV(json_single_data, 'sourceUpdateTime')
                instr_code = self.common.searchDicKV(json_single_data, 'code')
                # self.sq.subscribe_new_record(rev_data.type, instr_code, req_source_time, json_single_data)
        # print('AppQuoteAllApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # 手机Api---查询K线数据
    async def QueryKLineMsgReqApi(self, exchange, code, peroid_type, type, direct, start, end):
        now_timestamp = int(time.time() * 1000)  # 毫秒时间戳
        data_send = QueryKLineMsgReq(exchange=exchange, code=code, peroid_type=peroid_type, type=type, direct=direct, start=start, end=end, start_time_stamp=now_timestamp)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.QUERY_KLINE_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg)
        json_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.QUERY_KLINE_RSP:
                single_data = QueryKLineMsgRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                json_rsp_list.append(json_single_data)
        # print('QueryKLineMsgReqApi json_rsp_list:{}'.format(json_rsp_list))
        return json_rsp_list

    # app查询分时数据
    async def QueryKLineMinMsgReqApi(self, isSubKLineMin, exchange, code, query_type=None, direct=None, start=None, end=None, vol=None,
                                     start_time_stamp=None, recv_num=1, sub_quote_type=SubQuoteMsgType.REAL_QUOTE_MSG):
        # app订阅服务中，该api只会自动返回当天的分时数据，与入参无关
        '''
        message QueryKLineMinMsgReq
        {
            bool                  isSubKLineMin = 1;    // 是否订阅KLineMin
            common.ExchangeType   exchange      = 2;    // 交易所
            string                code          = 3;    // 合约代码
            QueryKLineMsgType     type          = 4;    // 获取K线的方式
            QueryKLineDirectType  direct        = 5;    // 查询K线的方向
            uint64                start         = 6;    // 开始时间
            uint64                end           = 7;    // 结束时间
            uint64                vol           = 8;    // 按量查询时此字段表示多少根
            uint64                start_time_stamp = 9; // 发起请求的时间戳 UTC时间戳
        }
        '''
        await self.HearbeatReqApi(connid=10086, isKeep=True)   # 避免循环接消息时心跳断掉
        data_send = QueryKLineMinMsgReq(isSubKLineMin=isSubKLineMin, exchange=exchange, code=code, type=query_type,
                                        direct=direct, start=start, end=end, vol=vol, start_time_stamp=start_time_stamp, sub_quote_type=sub_quote_type)
        quote_msg = QuoteMsgCarrier(type=QuoteMsgType.QUERY_KLINE_MIN_REQ, data=data_send.SerializeToString())
        quote_msg = quote_msg.SerializeToString()
        all_req = await self.client.send_and_recv(quote_msg, recv_num=recv_num)
        final_rsp = {}
        query_kline_min_rsp_list = []
        sub_kline_min_rsp_list = []
        for base_req in all_req:
            rev_data = QuoteMsgCarrier()
            rev_data.ParseFromString(base_req)
            if rev_data.type == QuoteMsgType.QUERY_KLINE_MIN_RSP:
                single_data = QueryKLineMinMsgRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                query_kline_min_rsp_list.append(json_single_data)
            elif rev_data.type == QuoteMsgType.SUBSCRIBE_KLINE_MIN_RSP:
                single_data = SubscribeKlineMinRsp()
                single_data.ParseFromString(rev_data.data)
                json_single_data = json_format.MessageToJson(single_data)
                json_single_data = json.loads(json_single_data)
                sub_kline_min_rsp_list.append(json_single_data)
        final_rsp['query_kline_min_rsp_list'] = query_kline_min_rsp_list
        final_rsp['sub_kline_min_rsp_list'] = sub_kline_min_rsp_list
        # print(final_rsp)
        return final_rsp

if __name__ == '__main__':
    common = Common()

