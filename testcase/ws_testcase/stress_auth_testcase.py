# -*- coding: utf-8 -*-
# !/usr/bin/python

from websocket_py3.ws_api.auth_api import *
from common.common_method import *
from multiprocessing import Pool, cpu_count
from pb_files.common_type_def_pb2 import *


class AuthStressTestCases(object):
    def __init__(self, thread_task_num, coroutine_task_num):
        self.group_task = GroupTask()
        self.common = self.group_task.common
        self.thread_task_num = thread_task_num
        self.coroutine_task_num = coroutine_task_num

    def test_001_auth(self, no_use):
        async def do_single_work(index, new_loop):
            result = {}
            result['ret'] = False
            try:
                api = AuthApi(auth_ws_url, new_loop, extra_headers=auth_headers)
                await api.client.ws_connect()

                start_time = time.time()
                auth_rspList = await api.AuthReqApi(token=str(market_token))
                result['auth_time'] = time.time() - start_time

                # await api.client.stress_disconnect()

                if auth_rspList[0]['retResult']['retCode'] == RetCode.Name(RetCode.SUCCESS):
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
        max_auth_time, min_auth_time, av_auth_time, all_auth_time = 0.0, 1000.0, 0.0, 0.0
        success_times = 0
        for info in info_list:
            try:
                if info['ret'] == True:
                    auth_time = info['auth_time']
                    success_times = success_times + 1
                    max_auth_time = max(auth_time, max_auth_time)
                    min_auth_time = min(auth_time, min_auth_time)
                    all_auth_time = all_auth_time + auth_time
            except Exception:
                print('Get error info to analyse:', info)
            if success_times:
                av_auth_time = float(all_auth_time / success_times)
            else:
                print('get no success response!!!')

        print('Get {} responses to analys'.format(info_list.__len__()))
        print('max_auth_time:{}s, min_auth_time:{}s, av_auth_time:{}s'.format(round(max_auth_time, 3),
                                                                              round(min_auth_time, 3),
                                                                              round(av_auth_time, 3)))
        return {'success_num': success_times}


if __name__ == '__main__':
    pass