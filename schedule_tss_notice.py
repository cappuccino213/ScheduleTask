"""
@File : schedule_technical_support_statistics_notice.py
@Date : 2023/6/27 16:23
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import time
from calendar import monthrange
from datetime import datetime

import requests

"""定时进行技术支持汇总统计的通知"""


class TechnicalSupportStatisticsNotice:
    def __init__(self):
        self.tss_source_api = "http://192.168.1.45:8087/tech-sup-chart/summary/notice"

    # 获取当月时间范围
    @staticmethod
    def get_month_range():
        now = datetime.now().date()
        month_first_day = datetime(now.year, now.month, 1)
        month_last_day = datetime(now.year, now.month, monthrange(now.year, now.month)[1])
        return month_first_day.strftime("%Y-%m-%d"), month_last_day.strftime("%Y-%m-%d")

    # 调用通知接口,本月通知
    def call_tss_notice_api(self):
        print(f"{6 * '='}技术支持统计通知{6 * '='}")
        time_range = TechnicalSupportStatisticsNotice.get_month_range()
        payload = {
            "startDate": time_range[0],
            "endDate": time_range[1],
            "sender": "",
            "auth_code": "",
            "recipients": []
        }
        header = {"Content-Type": "application/json"}
        res = requests.post(url=self.tss_source_api, json=payload, headers=header)
        print(res.json())


if __name__ == "__main__":
    pass
