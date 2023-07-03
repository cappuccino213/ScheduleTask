"""
@File : schedule_execute.py
@Date : 2023/6/6 15:52
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from apscheduler.schedulers.blocking import BlockingScheduler

from schedule_ts_commit import technical_support_record

from schedule_tss_notice import TechnicalSupportStatisticsNotice

from schedule_weekly_report import sync_weekly_task

from schedule_rdm_basedata import ProjectManage


def main():
    my_schedule = BlockingScheduler()

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

    """4.项目信息同步，每周一~周五，每十分钟执行一次"""
    my_schedule.add_job(ProjectManage().async_project_data, 'cron', day_of_week='mon-fri', minute='*/10')

    # 开始执行
    my_schedule.start()


if __name__ == "__main__":
    main()
