"""
@File : schedule_execute.py
@Date : 2023/6/6 15:52
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
# import datetime
# import threading

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from schedule_ts_commit import technical_support_record

from schedule_tss_notice import TechnicalSupportStatisticsNotice

from schedule_weekly_report import sync_weekly_task

from schedule_rdm_basedata import ProjectManage

from utility import *


def main():
    Toolkit.print_thread_info("我是主线程")
    job_defaults = {'max_instances': 10}  # 解决有任务执行失败后，最大实例数不够用的问题
    executors = {"default": ThreadPoolExecutor(5)}  # 设置线程池数量，比任务数多一，则始终任务不会miss
    my_schedule = BlockingScheduler(job_defaults=job_defaults, executors=executors)

    """1.技术支持记录提交任务,每隔30秒执行一次"""
    my_schedule.add_job(technical_support_record, 'interval', seconds=30, id='technical_support_record')
    # 每天下班时间执行
    # my_schedule.add_job(technical_support_record, 'cron', hour=17, minute=31)

    """2.技术支持统计邮件通知任务"""
    my_schedule.add_job(TechnicalSupportStatisticsNotice().call_tss_notice_api, 'cron', day='last', hour=17,
                        minute=25)

    # my_schedule.add_job(TechnicalSupportStatisticsNotice().call_tss_notice_api, 'interval', seconds=5,
    #                     id='call_tss_notice_api')

    """3.测试周报任务同步，每周一~周六，每十分钟执行一次"""
    my_schedule.add_job(sync_weekly_task, 'cron', day_of_week='mon-sat', minute='*/10')
    # my_schedule.add_job(sync_weekly_task, 'cron', day_of_week='mon-sat', second='*/10')

    """4.项目信息同步，每周一~周五，每半小时执行一次"""
    # my_schedule.add_job(ProjectManage().async_project_data, 'cron', day_of_week='mon-fri', second='*/15')
    my_schedule.add_job(ProjectManage().async_project_data, 'cron', day_of_week='mon-fri', minute='*/30')

    # 开始执行
    my_schedule.start()


if __name__ == "__main__":
    main()
