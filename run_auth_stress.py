# -*- coding: utf-8 -*-
# !/usr/bin/python

from testcase.ws_testcase.stress_auth_testcase import *


if __name__ == '__main__':
    print('Env is:', env)
    thread_task_num = int(all_task_num / process_num)
    item = AuthStressTestCases(thread_task_num=thread_task_num, coroutine_task_num=coroutine_task_num)
    inputList = []
    for i in range(process_num):
        inputList.append(i)
    pool = Pool(process_num)
    print('Start to run pressing test, plz wait!')
    start = time.time()
    all_analyse_info = pool.map(item.test_001_auth, inputList)
    pool.close()
    pool.join()
    end = time.time()
    print('all_task_num is: {}'.format(all_task_num))
    analyse_result = item.analyse(all_analyse_info)
    print('Pressing test time: {} sec'.format(round(end - start, 3)))
    print('TPS: {} per second'.format(round(analyse_result['success_num'] / (end - start), 3)))
    print('Successfull rate: {}%'.format(round(float(analyse_result['success_num'] / all_task_num), 4) * 100))