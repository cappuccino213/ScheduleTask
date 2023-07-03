"""
@File : schedule_rdm_basedata.py
@Date : 2023/6/30 15:41
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import requests
import datetime

from database_model import ProjectModel, UserModel, add_column, update_column, query_by_primary_key, ProductModel

"""研发管理系统基础数据相关"""


class ProjectManage:
    def __init__(self):
        self.fetch_task_host = "http://192.168.1.19:8889"
        self.rdm_host = "http://192.168.1.45:8086"

    # 从禅道获取当年项目
    def fetch_post(self):
        payload = dict(begin=datetime.date.today().strftime('%Y-01-01'), end=datetime.date.today().strftime('%Y-12-31'))
        result = requests.post(url=self.fetch_task_host + "/ewordci/project/list", json=payload,
                               headers={'Content-Type': 'application/json'})
        # print(result.json())
        return result.json()

    # 同步项目数据
    def async_project_data(self):
        print(f"{6 * '='}项目信息同步{6 * '='}")
        # 获取项目列表
        project_list = self.fetch_post()['data']
        if project_list:
            for project in project_list:
                # 查询是否有rmd库中是否处在,不存在就增加
                if_exist_project = ProjectModel.query_project(dict(ZTID=project['id']))
                project_dict = {'ProjectName': project['name'],
                                'LeaderID': UserModel.query_user_info(dict(ZTAccount=project['Leader'])).ID,
                                'ProductID': ProductModel.query_product(dict(ZTID=project['product'])).ID,
                                'State': 1 if project['status'] in ('wait', 'doing') else 2,
                                'ZTID': project['id'],
                                'CreateDate': project['createDate'],
                                'CreateUser': UserModel.query_user_info(dict(ZTAccount=project['createUser'])).ID,
                                'UpdateDate': datetime.datetime.today(),
                                'UpdateUser': 114
                                }
                if not if_exist_project:
                    add_column(ProjectModel(project_dict))
                    print(f"增加项目记录成功，详情{ProjectModel(project_dict).to_dict()}")
                # 存在就更新
                else:
                    project_dict['ID'] = if_exist_project.ID
                    update_column(project_dict, ProjectModel)


if __name__ == "__main__":
    # ProjectManage().fetch_post()
    ProjectManage().async_project_data()
