"""
@File : schedule_weekly_report.py
@Date : 2023/6/12 10:43
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import requests

from datetime import datetime, date, timedelta

from database_model import *

from utility import Toolkit

"""用于定时获取禅道的工作任务，同步到rdm的周报模块中"""


class WeeklyReport:
    def __init__(self):
        self.fetch_task_host = "http://192.168.1.19:8889"
        self.rdm_host = "http://192.168.1.45:8086"

    """获取任务相关"""

    # 定义一个获取任务的post方法
    def fetch_post(self, api_path, payload: dict):
        result = requests.post(url=self.fetch_task_host + api_path, json=payload,
                               headers={'Content-Type': 'application/json'})
        return result

    # 获取本周周一和周日日期
    @classmethod
    def this_monday_and_sunday(cls):
        """
        :return: 本周一和周日的日期
        """
        today = date.today()
        monday = datetime.strftime(today - timedelta(today.weekday()), '%Y-%m-%d')
        sunday = datetime.strftime(today + timedelta(7 - today.weekday() - 1), '%Y-%m-%d')
        return monday, sunday

    # 获取本周完成的测试单列表
    def fetch_this_week_test_task(self, user):
        payload = dict(begin=WeeklyReport.this_monday_and_sunday()[0], end=WeeklyReport.this_monday_and_sunday()[1],
                       owner=user)
        task_list = self.fetch_post("/ewordci/testtask/list", payload)
        if task_list.json()['data']:
            return task_list.json()['data']

    # 获取本周的处理的需求
    def fetch_this_week_demand(self, user):
        payload = dict(begin=WeeklyReport.this_monday_and_sunday()[0], end=WeeklyReport.this_monday_and_sunday()[1],
                       owner=user)
        story_list = self.fetch_post("/ewordci/story/list", payload)
        if story_list.json()['data']:
            return story_list.json()['data']

    # 获取自动同步的用户信息，当前版本可先暂时获取测试用户
    def fetch_users(self):
        users = requests.get(self.fetch_task_host + "/ewordci/user/qa_users/get")
        if users.json()['data']:
            return users.json()['data']

    # 根据测试单号获取报告信息
    def fetch_test_report(self, task):
        report = self.fetch_post("/ewordci/testreport/info", {'tasks': task})
        if report.json()['data']:
            return report.json()['data']

    # 根据产品和需求获取项目信息
    def fetch_project_story(self, project_story):
        story_info = self.fetch_post("/ewordci/projectstory/info", project_story)
        if story_info.json()['data']:
            return story_info.json()['data']

    """周报同步相关"""

    # 获取当前处于今年的第几周
    @staticmethod
    def count_week_of_this_year():
        calendar = datetime.now().isocalendar()
        return f"{calendar[0]}年第{calendar[1]}周"

    # 获取接口登录凭证
    def login(self, account_info: dict):
        """
        :param account_info: e.g.{'account':'jacky','password':'xxxxxxx'}
        :return:
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        parameter = dict(account=account_info['account'], password=account_info['password'])
        response = requests.post(url=self.rdm_host + "/api/User/Login", headers=headers, data=parameter).json()
        return response['data']

    # 获取当前周报
    def get_current_weekly_report(self, token):
        current_weekly = requests.get(self.rdm_host + "/api/Weekly/GetWeekly",
                                      params=dict(WeeklyDateFlag=date.today(),
                                                  WeeklyDate=self.count_week_of_this_year()),
                                      headers=dict(Authorization=token))
        return current_weekly.json()


# 同步测试周报任务
def sync_weekly_task():
    # 获取执行任务用户数据
    print(f"{6 * '='}测试周报任务同步{6 * '='}")
    wrt = WeeklyReport()
    task_users = wrt.fetch_users()
    print(f"1获取到用户数:{len(task_users)}")
    if task_users:
        for user in task_users:
            # 获取当前周报信息
            login_data = wrt.login(user)
            weekly_info = wrt.get_current_weekly_report("Bearer " + login_data['token'])

            # 项目总结表提交
            wps_dict = {'WeeklyID': weekly_info['data']['weeklyData']['weeklyID']}

            """测试单任务"""
            test_task = wrt.fetch_this_week_test_task(user['account'])
            if test_task:
                for task in test_task:
                    print(f"2-1获得用户{user['account']}的测试单任务：{task}")
                    """提交数据"""
                    # 项目总结表提交
                    wps_dict['ProjectID'] = ProjectModel.query_project(dict(ZTID=task['project'])).ID  # 项目id需要用rdm上的
                    wps = WeeklyProjectSummary.query_wps(wps_dict)
                    if not wps:  # 若不存在周报id和项目id相同的项目总结，则添加
                        add_column(WeeklyProjectSummary(wps_dict))
                        # 增加项目总结记录后重新获取ProjectSummaryID
                        wps = WeeklyProjectSummary.query_wps(wps_dict)

                    # 获取测试报告
                    relate_report = WeeklyReport().fetch_test_report(task['id'])
                    relate_report_id = relate_report['id'] if relate_report else ''

                    tt_dict = {
                        'TaskType': '1',  # 周任务表,TaskType：1-功能测试、2-性能测试、3-接口测试，ZTID：禅道测试单id
                        'ZTID': task['id'],
                        'WeeklyID': weekly_info['data']['weeklyData']['weeklyID'],
                        'Name': task['name'],
                        'ProjectSummaryID': wps.ID,
                        'TaskDescrible': Toolkit.parse_html(task['desc']),
                        'ActualStartDate': task['begin'],
                        'ActualDeadLine': task['end'],
                        # 'TaskStatus': '4',
                        'TaskStatus': '2' if task['status'] == 'doing' else '4' if task['status'] == 'done' else '',
                        'DutyUserID': login_data['userID'],
                        'RelateTestBill': str(task['id']),
                        # 'RelateReport': str(WeeklyReport().fetch_test_report(task['id'])['id']),
                        'RelateReport': relate_report_id,
                        'AddUserID': login_data['userID']
                    }
                    wt = WeeklyTask.query_wt(tt_dict)
                    if not wt:  # 若不存在相同类型的功能测试单，则添加
                        add_column(WeeklyTask(tt_dict))
                        print(f"3-1增加WeeklyTask表测试单成功，记录详情{tt_dict}")
                    else:  # 若存在则修改
                        tt_dict['ID'] = wt.ID
                        update_column(tt_dict, WeeklyTask)
                        print(f"3-1更新WeeklyTask表测试单成功，记录详情{tt_dict}")

            """需求任务"""
            # 获取当前用户需求任务
            demand_task = wrt.fetch_this_week_demand(user['account'])
            if demand_task:  # 若不存在相同的需求任务，则添加到任务表
                for demand in demand_task:
                    print(f"2-1获得用户{user['account']}的需求处理任务：{demand}")
                    # 获取项目ID
                    project_zt_id = wrt.fetch_project_story(dict(product=demand['product'], story=demand['id']))[
                        'project']
                    wps_dict['ProjectID'] = ProjectModel.query_project(dict(ZTID=project_zt_id)).ID
                    wps = WeeklyProjectSummary.query_wps(wps_dict)
                    if not wps:
                        add_column(WeeklyProjectSummary(wps_dict))
                        wps = WeeklyProjectSummary.query_wps(wps_dict)

                    # 需求提交任务信息
                    st_dict = {
                        'TaskType': 'released' if demand['stage'] == "released" else
                        'confirm' if demand['status'] == 'draft' else 'review',  # 根据需求阶段或需求状态来确定任务类型为发布、确认或评审
                        'ZTID': demand['id'],
                        'WeeklyID': weekly_info['data']['weeklyData']['weeklyID'],
                        'Name': demand['title'],
                        'ProjectSummaryID': wps.ID,
                        # 'TaskDescrible': f"详情见禅道需求#{demand['id']}",
                        'TaskDescrible': f"http://192.168.1.43:8086/zentao/story-view-{demand['id']}.html",
                        'ActualStartDate': demand['lastEditedDate'],
                        'ActualDeadLine': demand['lastEditedDate'],
                        'TaskStatus': '4',
                        'DutyUserID': login_data['userID'],
                        'RelateTestBill': '',
                        'RelateReport': '',
                        'AddUserID': login_data['userID']
                    }
                    wt = WeeklyTask.query_wt(st_dict)
                    if not wt:
                        add_column(WeeklyTask(st_dict))
                        print(f"3-1增加WeeklyTask表需求处理记录成功，记录详情{st_dict}")
                    else:  # 若存在则修改
                        st_dict['ID'] = wt.ID
                        update_column(st_dict, WeeklyTask)
                        print(f"3-1更新WeeklyTask表需求处理记录成功，记录详情{st_dict}")


if __name__ == "__main__":
    # print(WeeklyReport.this_monday_and_sunday)
    # wr = WeeklyReport()
    # print(wr.fetch_this_week_test_task())
    # print(wr.get_current_weekly_report(wr.api_token({'account': 'zyp', 'password': 'c25e4bd763ef8450d506ed9288557cc0'})))
    # print(wr.get_current_weekly_report(
    #     wr.api_token({'account': 'zhangl', 'password': '4a1f7e0f07ca9c220014f0e75641e94c'})))
    # print(wr.count_week_of_this_year())
    sync_weekly_task()
