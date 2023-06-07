"""
@File : schedule_ts_notice.py
@Date : 2023/5/30 17:04
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import calendar
import datetime

import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


# 获取当月时间范围
def get_month_range():
    now = datetime.now().date()
    month_first_day = datetime(now.year, now.month, 1)
    month_last_day = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    return month_first_day.strftime("%Y-%m-%d"), month_last_day.strftime("%Y-%m-%d")


# job1：每月最后一天自动发送当月的统计数据
def job_ts_notice(start_date, end_date):
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "sender": "",
        "auth_code": "",
        "recipients": []
    }
    header = {"Content-Type": "application/json"}
    res = requests.post(url="http://192.168.1.45:8087/tech-sup-chart/summary/notice", json=payload, headers=header)
    print(res.json())


# job2：时间打印任务，为标记计划执行中
def job_print_time():
    print(f"技术统计任务执行中，当前时间{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# 执行job
def main():
    my_schedule = BlockingScheduler()
    my_schedule.add_job(job_print_time, 'interval', seconds=10, id='print_time')
    this_month_range = get_month_range()
    # 每个月的最后一天触发，下班时间执行,测试
    # my_schedule.add_job(job_ts_notice, 'cron', day=30, hour=17, minute=25,
    #                     args=[this_month_range[0], this_month_range[1]])
    my_schedule.add_job(job_ts_notice, 'cron', day='last', hour=17, minute=25,
                        args=[this_month_range[0], this_month_range[1]])

    my_schedule.start()


if __name__ == "__main__":
    main()
