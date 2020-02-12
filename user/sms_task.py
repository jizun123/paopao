import json
import requests
import hashlib
import  time
import base64
from django.conf  import settings
def send_sms(phone, code):
    # 发送手机验证码
    try:
        accountId = settings.SMS_ACCOUNT_ID
        token_id = settings.SMS_TOKEN_ID
        time_str = time.strftime("%Y%m%d%H%M%S", time.localtime())

        m = hashlib.md5()
        m.update((accountId + token_id + time_str).encode())
        sigParameter = m.hexdigest()

        author_str = base64.urlsafe_b64encode((accountId + ':' + time_str).encode())

        headers = {
            'Host': '192.168.0.1:8883',
            'Accept': 'application/json',
            'content-length': '139',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': author_str
        }
        data_str = {
            'to': phone,
            'appId': settings.SMS_APP_ID,
            'templateId': '1',
            'datas': [code, settings.SMS_VALID_TIME],
        }
        smg = requests.post(
            url='https://app.cloopen.com:8883/2013-12-26/Accounts/{0}/SMS/TemplateSMS?sig={1}'.format(accountId,sigParameter),
            headers=headers, data=json.dumps(data_str))

        print('----send sms ok-----')
        # b2b  连调时，需要在完成任务时，通知一下对方公司
    except Exception as e:
        print('--send sms error--')
        print(e)
        # TODO 上线后添加 error response


