"""
@File : schedule_rdm.py
@Date : 2023/5/31 14:56
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import os
import shutil

import requests
import xlrd as xlrd


class DevelopmentManager:
    def __init__(self, account, password):
        self.host = "http://192.168.1.45:8086"
        self.account = account
        self.password = password

    # 登录获取token
    def login(self):
        api = "/api/User/Login"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        parameter = dict(account=self.account, password=self.password)
        response = requests.post(url=self.host + api, headers=headers, data=parameter)
        return response.json()

    # 定义一个get方法
    def request_get(self, api):
        headers = dict(Authorization="Bearer " + self.login()['data']['token'])
        # print(headers)
        return requests.get(self.host + api, headers=headers).json()['data']

    # 获取产品数据
    def get_product(self):
        res = self.request_get("/api/Product/GetProductSelectData")
        return res['productData']

    # 获取记录人数据
    def get_record_users(self):
        res = self.request_get("/api/User/GetUserSelectDataByProType?type=0")
        return res['userData']

    # 获取提问人
    def get_post_users(self):
        res = self.request_get("/api/User/GetUserSelectDataByProType?type=1")
        return res['userData']

    # 获取项目数据
    def get_project_data(self):
        res = self.request_get("/api/Project/GetProjectSelectDataByType?type=1")
        return res['projectSelect']

    # 获取咨询问题类型
    def get_problem_type(self):
        res = self.request_get("/api/Records/GetProblemTypeSelect")
        return res['problemTypeSelect']

    # 定义一个form格式的post方法
    def request_post(self, api, params):
        headers = {
            'Authorization': 'Bearer ' + self.login()['data']['token'],
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # print(headers)
        return requests.post(url=self.host + api, headers=headers, data=params).json()


class ExcelObject:
    def __init__(self, file_path):
        self.file_path = file_path

    # 读取excel内容
    def get_content(self):
        with xlrd.open_workbook(self.file_path) as workbook:
            sheet = workbook.sheet_by_name('records')  # 只获取第一个sheet的数据
            """获取表头和数据行，组成dict格式"""
            data = []
            for row in range(2, sheet.nrows):  # 从第3行开始获取
                value_list = sheet.row_values(row)  # 每行数据
                # """去除内容中的空格"""
                # for col in range(sheet.ncols):
                #     value_list[col] = str(value_list[col]).replace(" ", "")
                data.append(dict(zip(sheet.row_values(0), value_list)))
            return data

    # 获取账号和密码
    def get_account(self):
        with xlrd.open_workbook(self.file_path) as workbook:
            sheet = workbook.sheet_by_name('account')
            return dict(account=sheet.cell(1, 0).value, password=sheet.cell(1, 1).value)

    # 过滤出有效数据
    @staticmethod
    def filter_valid_list(column_list, required_fields):
        """
        :param column_list: 从excel读取的数据列表，get_content的返回结果
        :param required_fields: 表格中的必填项字段
        :return: 返回有效的数据列list
        """
        valid_data = []
        for column_data in column_list:
            valid_count = 0
            for field in required_fields:
                if column_data[field]:
                    valid_count += 1
            if len(required_fields) == valid_count:
                valid_data.append(column_data)
        return valid_data

    # 通过field_map，将字段名转化成字段值
    @staticmethod
    def field_to_id(field, mapping: list[dict]):
        """
        :param field: 字段名，如“南京栖霞区医院'”
        :param mapping:字段名和id的对应list，如[{'label': '阜阳市人民医院', 'value': 1064}, {'label': '南京栖霞区医院', 'value': 1065}, {'label': '梧州市人民医院', 'value': 1066}, {'label': '亳州市人民医院', 'value': 1067}]
        :return:id
        """
        field_id = 0
        for kv in mapping:
            if field in kv['label'] or field == kv['label']:
                field_id = kv['value']
                break
        return field_id

    # 将表格的时间转化成时间格式
    @staticmethod
    def float_to_datetime(num: float):
        date_obj = datetime.datetime(year=1900, month=1, day=1)
        date_obj += datetime.timedelta(days=num - 2)
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")


"""识别技术支持内容提交接口，提交后备份数据"""


# 程序根目录下找excel文件
# 这种方法会递归所有子目录查找
# def find_excel(dir_path=r'./'):
#     file_list = []
#     for root, dirs, files in os.walk(dir_path):
#         for file in files:
#             if file.endswith("xlsx"):
#                 file_list.append(os.path.join(root, file))
#     return file_list

def find_excel(dir_path=r'./'):
    dir_list = os.listdir(dir_path)
    file_list = []
    for file in dir_list:
        abs_path = os.path.join(dir_path, file)
        if os.path.isfile(abs_path):
            if abs_path.endswith('xlsx'):
                file_list.append(abs_path)
    return file_list


# 提交数据
def commit_ts():
    # 1 识别内容
    excel_list = find_excel()
    # 获取技术支持列表
    # ts_list = []
    commit_result = []
    for excel in excel_list:
        ts = ExcelObject(excel)
        records = ts.filter_valid_list(ts.get_content(),
                                       ['PostUserName', 'RecordTime', 'ProjectName', 'ProductName', 'content',
                                        'OperateName'])
        # 登录账号，创建研发系统接口对象
        dm = DevelopmentManager(ts.get_account()['account'], ts.get_account()['password'])
        # 将关键字段的id加入data
        # payload_list = []

        # 优先级无接口调用，故直接定义mapping
        priority_mapping = [{'label': '紧急', 'value': '0'}, {'label': '一般', 'value': '1'}]
        # 记录状态
        status_mapping = [{'label': '未处理', 'value': '0'}, {'label': '进行中', 'value': '1'},
                          {'label': '处理完', 'value': '2'}, {'label': '无法处理', 'value': '3'}]
        # commit_result = []
        for record in records:
            # 2 数据有效化
            # 设置字段mapping（项目、产品名称、用户等匹配id）
            record['PostUserID'] = ts.field_to_id(record['PostUserName'], dm.get_post_users())
            record['ProductID'] = ts.field_to_id(record['ProductName'], dm.get_product())
            record['ProjectID'] = ts.field_to_id(record['ProjectName'], dm.get_project_data())
            record['type'] = ts.field_to_id(record['TypeName'], dm.get_problem_type())
            record['OperateUserID'] = ts.field_to_id(record['OperateName'], dm.get_record_users())
            record['Priority'] = ts.field_to_id(record['Priority'], priority_mapping)
            record['Status'] = ts.field_to_id(record['Status'], status_mapping)
            # 对时间数据进行处理
            if record['RecordTime'] == '':
                record['RecordTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                record['RecordTime'] = ts.float_to_datetime(record['RecordTime'])
            if record['createTime'] == '':
                record['createTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                record['createTime'] = ts.float_to_datetime(record['createTime'])
            if record['finishHour'] == '':
                record['finishHour'] = 0
            res = dm.request_post("/api/Records/InsertRecord", record)
            commit_result.append(res)
    return commit_result


# 备份数据
def backup_excel_after_commit():
    backup_src_list = find_excel()
    count = 0
    backup_dst_list = []
    for backup_file in backup_src_list:
        dst = r'./backup/' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '-' + str(count) + '.xlsx'
        shutil.move(backup_file, dst)
        count += 1
        backup_dst_list.append(dst)
    return backup_dst_list


# 执行函数
def technical_support_record():
    print(f"提交记录，结果：\n{commit_ts()}")
    print(f"记录表备份成功，备份结果：\n{backup_excel_after_commit()}")


if __name__ == "__main__":
    """dm测试"""
    # dm = DevelopmentManager('zyp', 'c25e4bd763ef8450d506ed9288557cc0')
    # print(dm.login())
    # print(dm.get_record_users())
    # param1 = dict(postUserID=2184, RecordTime='2023-05-31 16:00:01.650', createTime='2023-05-31 16:00:01.650',
    #               content='测试问题2',
    #               replyContent='回答问题2', operateUserID=114)
    #
    # print(dm.request_post("/api/Records/InsertRecord", param1))

    """excel测试"""
    ec = ExcelObject(r"./技术支持张烨平.xlsx")
    # print(ec.field_to_id('张烨平', dm.get_record_users()))
    # print(ec.get_account())
    print(ec.get_content())
    #
    # print(find_excel(r'./'))

    """commit_ts测试"""
    # print(commit_ts())

    """备份文件测试"""
    # backup_excel_after_commit()
    # print(find_excel())
    # technical_support_record()
