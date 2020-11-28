# -*- coding: utf-8 -*-
# !/usr/bin/python

from multiprocessing import cpu_count

env = 'QA'

process_num = cpu_count() if cpu_count() < 6 else 6
# process_num = 1
coroutine_task_num = 25
x_num = 20
all_task_num = process_num * coroutine_task_num * x_num     # 请设置 任务数为 processNum * coroutine_task_num 的整数倍
test_market = 'HKFE'
if test_market == 'SEHK':
    test_code_list = ['00700', '09988', '01211', '01299', '02318', '00175', '00941', '03888', '03968', '03690']
elif test_market == 'HKFE':
    test_code_list = ['MHImain', 'HSImain', 'CUSmain', 'HHImain', 'MCHmain']
elif test_market == 'COMEX':
    test_code_list = ['GCmain', 'SImain', 'HGmain']



if env == 'QA':
    market_ws_url = 'ws://172.16.10.211:1516'
    market_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJtaWRkbGVfc2VydmVyIiwiZXhwIjoxNjA1NzEzMjcxLCJzdWIiOiIxNjA1NjcwMDcxMjMzIiwiY3VzdG9tIjoie1wiSU5URVJOQVRJT05BTF9GVVRVUkVTXCI6e1widGltZUxpbWl0XCI6XCIyMDIwLTExLTE4VDIzOjI3OjUxLjIzMzQwMzAwMFwiLFwibWFya2V0UmlnaHRUeXBlXCI6XCJSRUFMXCJ9LFwiSEtfU1RPQ0tTXCI6e1widGltZUxpbWl0XCI6XCIyMDIwLTExLTE4VDIzOjI3OjUxLjIzMzQwMTAwMFwiLFwibWFya2V0UmlnaHRUeXBlXCI6XCJSRUFMXCJ9LFwiSEtfRlVUVVJFU1wiOntcInRpbWVMaW1pdFwiOlwiMjAyMC0xMS0xOFQyMzoyNzo1MS4yMzM0MDIwMDBcIixcIm1hcmtldFJpZ2h0VHlwZVwiOlwiUkVBTFwifSxcIlVTX1NUT0NLU1wiOntcInRpbWVMaW1pdFwiOlwiMjAyMC0xMS0xOFQyMzoyNzo1MS4yMzM0MDMwMDBcIixcIm1hcmtldFJpZ2h0VHlwZVwiOlwiUkVBTFwifX0iLCJzY29wZSI6InF1b3RlcyJ9.QwyhnI-30Wge40XQM_iUB1aR3ytGy59zsPZ0d3hZfKeITTbUaVYyLnLPW72C6vY7LgM6LJAVP_upcB0yeI_i14agAVBn8ULQ23Aw2dNzRIg_IWSUSQpCugBbDk405WnNycSqyWxgOOIjI7Y6Tk_31DtT9jlUxZTwQWSVPH2kpyk'
    auth_ws_url = 'wss://eddid-auth-center-qa.eddid.com.cn:1443/ws'
    auth_headers = {
        "Authorization": "Basic cXVvdGVzX3NlcnZlcjoxMjM0"
    }

if env == 'DEV':
    market_ws_url = 'ws://172.16.10.207:11516'
    market_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJtaWRkbGVfc2VydmVyIiwiZXhwIjoxNjEzMzUzNDY1LCJzdWIiOiJkY2Q2ODg1MS1lMzY1LTQ1YTQtYWM0Mi01Njk2ZGRiMzIyZGUiLCJzY29wZSI6InF1b3RlcyJ9.IxUnD70BivbHERhxGxKr3GHR3U0LQ5NMrVuPhOInEN09gE2VQIlAduGjcafO9It1OzzCx8bwarFaRDATt5spTi3OBwE_kocfRMzn_sSpHffhyI__bJ0bG-a2kkr6v4F1KVpXVinWnZVYnnYB8WOHyiICAVgpaGdroPts3AoCU2w'
    # auth_ws_url = 'wss://eddid-auth-center-qa.eddid.com.cn:1443/ws'
    # auth_headers = {
    #     "Authorization": "Basic cXVvdGVzX3NlcnZlcjoxMjM0"
    # }

elif env == 'UAT':
    market_ws_url = 'ws://192.168.80.201:1516'
    market_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ0ZXN0YXBwMiIsImV4cCI6MTYwNDM5OTkyMywic3ViIjoiZTk3YTNjZDUtZWE0YS00MmU5LWFkN2MtNzY3NmQ0YmExODkzIiwic2NvcGUiOiJiYXNpYyJ9.T7_EeFlqqthV5Y4UVyofR4oUW9WVv27lY8BQDX58sMRbm6avxF7_T51oV_OtMHPAX6tAd-jHaweRYHLFQGLP5T21jWISJfHYHYP0VflPITQKX6v9s9Bx4AqLBNokkJUI5a7AORr0cIcSQVMRrzHVwEB9jV7rXjRXmgDLQa1g70c'
    auth_ws_url = 'wss://eddid-auth-center-uat.eddid.com.cn:1443/ws'
    auth_headers = {
        "Authorization": "Basic cXVvdGVzX3NlcnZlcjoxMjM0"
    }

elif env == 'PRD':
    market_ws_url = 'ws://47.112.190.83:11516'
    market_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJtaWRkbGVfc2VydmVyIiwiZXhwIjoxNjA3MDQ4NjY5LCJzdWIiOiIzY2UzZGMzYS05ZGE2LTQ3NzAtOGM3OS0xYTI4OWVkZTBkZWIiLCJjdXN0b20iOiJ7XCJJTlRFUk5BVElPTkFMX0ZVVFVSRVNcIjp7XCJ0aW1lTGltaXRcIjpcIjIwMjAtMTItMDRUMTA6MjQ6MjkuMjU5NDM1MDAwXCIsXCJtYXJrZXRSaWdodFR5cGVcIjpcIlJFQUxcIn0sXCJIS19TVE9DS1NcIjp7XCJ0aW1lTGltaXRcIjpcIjIwMjAtMTItMDRUMTA6MjQ6MjkuMjU5NDMyMDAwXCIsXCJtYXJrZXRSaWdodFR5cGVcIjpcIlJFQUxcIn0sXCJIS19GVVRVUkVTXCI6e1widGltZUxpbWl0XCI6XCIyMDIwLTEyLTA0VDEwOjI0OjI5LjI1OTQzMzAwMFwiLFwibWFya2V0UmlnaHRUeXBlXCI6XCJSRUFMXCJ9LFwiVVNfU1RPQ0tTXCI6e1widGltZUxpbWl0XCI6XCIyMDIwLTEyLTA0VDEwOjI0OjI5LjI1OTQzNTAwMFwiLFwibWFya2V0UmlnaHRUeXBlXCI6XCJSRUFMXCJ9fSIsInNjb3BlIjoicXVvdGVzIn0.LmSjaaDA6SHZdAs4MwpkwHR6JIpiRBTSGQ4AAQigRkOUO2fepfnQS7v-Kth2HVoUsZWINFiHPcnsEsve1E7iFIcZTTqfMBC1R3ZEKjyWgvTKnYaqG0JvnaN_IMhOzqF3SlZIesH0px2U16XWEYpI9e66V55JLeSGtjmcrxBsaCw'

