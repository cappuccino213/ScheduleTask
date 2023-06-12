"""
@File : schedule_execute.py
@Date : 2023/6/6 15:52
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from apscheduler.schedulers.blocking import BlockingScheduler

from schedule_ts_commit import technical_support_record
from schedule_ts_commit import datetime
from schedule_ts_notice import job_ts_notice
from schedule_ts_notice import get_month_range


# 用于任务执行标记
def job_print_time():
    print(f"技术支持数据任务执行中，当前时间{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    my_schedule = BlockingScheduler()
    # 任务运行标记
    my_schedule.add_job(job_print_time, 'interval', seconds=10, id='print_time')

    """1.技术支持记录提交任务"""
    my_schedule.add_job(technical_support_record, 'interval', seconds=10, id='technical_support_record')
    # 每天下班时间执行
    # my_schedule.add_job(technical_support_record, 'cron', hour=17, minute=31)

    """2.技术支持统计邮件通知任务"""
    my_schedule.add_job(job_ts_notice, 'cron', day='last', hour=17, minute=25,
                        args=[get_month_range()[0], get_month_range()[1]])

    my_schedule.start()


if __name__ == "__main__":
    main()
