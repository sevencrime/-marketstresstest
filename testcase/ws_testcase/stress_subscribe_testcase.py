# -*- coding: utf-8 -*-
# !/usr/bin/python

from websocket_py3.ws_api.subscribe_server_api import *
from common.common_method import *
from multiprocessing import Pool, cpu_count
from pb_files.common_type_def_pb2 import *


class SubscribeStressTestCases(object):
    def __init__(self, thread_task_num, coroutine_task_num):
        self.group_task = GroupTask()
        self.common = self.group_task.common
        self.thread_task_num = thread_task_num
        self.coroutine_task_num = coroutine_task_num

    def test_001_login(self, no_use):
        async def do_single_work(index, new_loop):
            result = {}
            result['ret'] = False
            try:
                api = SubscribeApi(market_ws_url, new_loop)
                start_time = time.time()
                await api.client.ws_connect()
                result['connect_time'] = time.time() - start_time
                start_time = time.time()
                login_rspList = await api.LoginReq(token=str(market_token), start_time_stamp=int(time.time() * 1000))
                # print(login_rspList)
                result['login_time'] = time.time() - start_time
                exchange = test_market

                # for i in range(test_code_list.__len__()):
                code = test_code_list[0]
                start_time = time.time()
                query_rsp = await api.QueryKLineMinMsgReqApi(isSubKLineMin=False, exchange=exchange, code=code)
                result['query_rsp_time'] = time.time() - start_time

                for i in range(test_code_list.__len__()):
                    code = test_code_list[i]
                    start_time = time.time()
                    quote_rsp_single = await api.SubsQutoMsgReqApi(sub_type=SubscribeMsgType.SUB_WITH_MSG_DATA,
                                                            child_type=SubChildMsgType.SUB_SNAPSHOT,
                                                            base_info=[{'exchange': exchange, 'code': code}],
                                                          start_time_stamp=int(time.time() * 1000))
                    if i == 0:
                        quote_rsp = quote_rsp_single
                        result['sub_rsp_time'] = time.time() - start_time

                start_time = time.time()
                snap_list = []
                for j in range(2000):
                    snap_list = await api.QuoteSnapshotApi(recv_num=5)
                recv_time = float(snap_list[-1]['commonInfo']['publisherRecvTime']) / 1000
                source_time = float(snap_list[-1]['sourceUpdateTime']) / pow(10, 9)

                result['recv_snapshot_time'] = time.time() - source_time
                start_time = time.time()
                await api.client.stress_disconnect()
                result['disconnect_time'] = time.time() - start_time
                if login_rspList[0]['retResult']['retCode'] == RetCode.Name(RetCode.CHECK_TOKEN_SUCCESS) and \
                        quote_rsp['first_rsp_list'][0]['retResult']['retCode'] == 'SUCCESS' and \
                        query_rsp['query_kline_min_rsp_list'][0]['retResult']['retCode'] == 'SUCCESS':
                    result['ret'] = True
                else:
                    result['ret'] = False
            except Exception as e:
                print('do_single_work error: ', e)
            finally:
                return result

        group_tasks = []
        work_loop = self.common.getNewLoop()
        workers_threads = []
        analyse_info = []
        for i in range(self.thread_task_num):
            if (i + 1) % self.coroutine_task_num == 0:
                group_tasks.append(do_single_work(i, work_loop))
                workers_threads.append(self.group_task.group_worker(group_tasks))
                group_tasks = []
                work_loop = None
            else:
                if work_loop == None:
                    work_loop = self.common.getNewLoop()
                group_tasks.append(do_single_work(i, work_loop))
        self.group_task.start_group_worker(workers_threads)
        self.group_task.join_group_worker(workers_threads)
        for work in workers_threads:
            analyse_info = analyse_info + work.result
        return analyse_info

    def analyse(self, analyse_info_list):
        print('Start analysing!')
        info_list = []
        for analyse_info in analyse_info_list:
            info_list = info_list + analyse_info
        max_connect_time, min_connect_time, av_connect_time, all_connect_time = 0.0, 1000.0, 0.0, 0.0
        max_login_time, min_login_time, av_login_time, all_login_time = 0.0, 1000.0, 0.0, 0.0
        max_query_rsp_time, min_query_rsp_time, av_query_rsp_time, all_query_rsp_time = 0.0, 1000.0, 0.0, 0.0
        max_sub_rsp_time, min_sub_rsp_time, av_sub_rsp_time, all_sub_rsp_time = 0.0, 1000.0, 0.0, 0.0
        max_recv_snapshot_time, min_recv_snapshot_time, av_recv_snapshot_time, all_recv_snapshot_time = 0.0, 1000.0, 0.0, 0.0
        max_disconnect_time, min_disconnect_time, av_disconnect_time, all_disconnect_time = 0.0, 1000.0, 0.0, 0.0
        success_times = 0
        for info in info_list:
            try:
                if info['ret'] == True:

                    connect_time = self.common.doDicEvaluate(info, 'connect_time', 0)
                    login_time = self.common.doDicEvaluate(info, 'login_time', 0)
                    disconnect_time = self.common.doDicEvaluate(info, 'disconnect_time', 0)
                    query_rsp_time = self.common.doDicEvaluate(info, 'query_rsp_time', 0)
                    sub_rsp_time = self.common.doDicEvaluate(info, 'sub_rsp_time', 0)
                    recv_snapshot_time = self.common.doDicEvaluate(info, 'recv_snapshot_time', 0)

                    success_times = success_times + 1
                    max_connect_time = max(connect_time, max_connect_time)
                    min_connect_time = min(connect_time, min_connect_time)
                    all_connect_time = all_connect_time + connect_time

                    max_login_time = max(login_time, max_login_time)
                    min_login_time = min(login_time, min_login_time)
                    all_login_time = all_login_time + login_time

                    max_query_rsp_time = max(query_rsp_time, max_query_rsp_time)
                    min_query_rsp_time = min(query_rsp_time, min_query_rsp_time)
                    all_query_rsp_time = all_query_rsp_time + query_rsp_time

                    max_sub_rsp_time = max(sub_rsp_time, max_sub_rsp_time)
                    min_sub_rsp_time = min(sub_rsp_time, min_sub_rsp_time)
                    all_sub_rsp_time = all_sub_rsp_time + sub_rsp_time

                    max_recv_snapshot_time = max(recv_snapshot_time, max_recv_snapshot_time)
                    min_recv_snapshot_time = min(recv_snapshot_time, min_recv_snapshot_time)
                    all_recv_snapshot_time = all_recv_snapshot_time + recv_snapshot_time

                    max_disconnect_time = max(disconnect_time, max_disconnect_time)
                    min_disconnect_time = min(disconnect_time, min_disconnect_time)
                    all_disconnect_time = all_disconnect_time + disconnect_time
            except Exception:
                print('Get error info to analyse:', info)
        if success_times:
            av_connect_time = float(all_connect_time / success_times)
            av_login_time = float(all_login_time / success_times)
            av_query_rsp_time = float(all_query_rsp_time / success_times)
            av_sub_rsp_time = float(all_sub_rsp_time / success_times)
            av_recv_snapshot_time = float(all_recv_snapshot_time / success_times)
            av_disconnect_time = float(all_disconnect_time / success_times)
        else:
            print('get no success response!!!')

        print('Get {} responses to analys'.format(info_list.__len__()))
        print('max_connect_time:{}s, min_connect_time:{}s, av_connect_time:{}s\n'
              'max_login_time:{}s, min_login_time:{}s, av_login_time:{}s\n'
              'max_query_rsp_time:{}s, min_query_rsp_time:{}s, av_query_rsp_time:{}s\n'
              'max_sub_rsp_time:{}s, min_sub_rsp_time:{}s, av_sub_rsp_time:{}s\n'
              'max_recv_snapshot_time:{}s, min_recv_snapshot_time:{}s, av_recv_snapshot_time:{}s\n'
              'max_disconnect_time:{}s, min_disconnect_time:{}s, av_disconnect_time:{}s'.format(round(max_connect_time, 3),
                                                                                                round(min_connect_time, 3),
                                                                                                round(av_connect_time, 3),
                                                                                                round(max_login_time, 3),
                                                                                                round(min_login_time, 3),
                                                                                                round(av_login_time, 3),
                                                                                                round(max_query_rsp_time, 3),
                                                                                                round(min_query_rsp_time, 3),
                                                                                                round(av_query_rsp_time, 3),
                                                                                                round(max_sub_rsp_time, 3),
                                                                                                round(min_sub_rsp_time, 3),
                                                                                                round(av_sub_rsp_time, 3),
                                                                                                round(max_recv_snapshot_time, 3),
                                                                                                round(min_recv_snapshot_time, 3),
                                                                                                round(av_recv_snapshot_time, 3),
                                                                                                round(max_disconnect_time, 3),
                                                                                                round(min_disconnect_time, 3),
                                                                                                round(av_disconnect_time, 3)))
        return {'success_num': success_times}


if __name__ == '__main__':
    pass