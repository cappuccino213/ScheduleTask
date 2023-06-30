"""
@File : database_model.py
@Date : 2023/6/19 14:55
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from urllib.parse import quote_plus
from sqlalchemy import create_engine, Column, Integer, String, DateTime, SmallInteger

from sqlalchemy.orm import sessionmaker, declarative_base

"""由于rdm系统的周报提交接口不好用，故直接通过数据库操作"""
# 定义一个数据库连接

Base = declarative_base()

engine = create_engine(f"mssql+pymssql://sa:{quote_plus('p@ssw0rd')}@192.168.1.45:1433/eWordRDM_dev",
                       # engine = create_engine(f"mssql+pymssql://sa:{quote_plus('p@ssw0rd')}@192.168.1.45:1433/eWordRDM_Imp",
                       pool_recycle=3600, echo=False)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()


# 通过主键查找
def query_by_primary_key(_id: int, model: Base):
    try:
        # 根据主键id查询
        return session.query(model).get(_id)
    except Exception as e:
        print(str(e))
    finally:
        session.close()


# 添加一行
def add_column(model: Base):
    try:
        session.add(model)
        session.commit()
        session.refresh(model)  # 为了读取自增字段(如果有的话)到对象
        session.expunge(model)
    except Exception as e:
        print(str(e))
        session.rollback()
        session.flush()
    finally:
        session.close()


# 修改表数据
def update_column(fields: dict, model: Base):
    if_exist = query_by_primary_key(fields['ID'], model)
    if if_exist:
        original_column = if_exist.to_dict()
        try:  # 使用遍历k,v方式对应赋值
            for k, v in fields.items():
                if original_column.get(k) != v:  # 判断是传入的值与原始值是否一样，不一样则更新，为了防止类型不同而修改强制转化成str
                    session.query(model).filter(model.ID == fields['ID']).update({k: v})
            session.commit()  # 提交修改
            session.flush()
            return update_column
        except Exception as e:
            print("update_column异常：" + str(e))
            session.rollback()
            session.flush()
        finally:
            session.close()


# 定义数据表模型
class WeeklyProjectSummary(Base):
    __tablename__ = 'T_WeeklyProjectSummary'
    ID = Column(Integer, primary_key=True)
    WeeklyID = Column(Integer)
    ProjectID = Column(Integer)
    DirectorSummary = Column(String, default=None)
    ManagerSummary = Column(String, default=None)

    def __init__(self, fields: dict):
        # self.ID = fields.get('id')
        self.WeeklyID = fields.get('WeeklyID')
        self.ProjectID = fields.get('ProjectID')
        self.DirectorSummary = fields.get('DirectorSummary')
        self.ManagerSummary = fields.get('ManagerSummary')

    # 根据条件查询
    @classmethod
    def query_wps(cls, condition: dict):
        try:
            result = session.query(cls)
            if condition.get('ID'):
                result = result.filter(cls.ID == condition.get('ID'))
            if condition.get('WeeklyID'):
                result = result.filter(cls.WeeklyID == condition.get('WeeklyID'))
            if condition.get('ProjectID'):
                result = result.filter(cls.ProjectID == condition.get('ProjectID'))
            # return result.all()
            return result.first()
        except Exception as e:
            print("query_wps异常：" + str(e))
        finally:
            session.close()

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# 项目
class Project(Base):
    __tablename__ = 'T_Project'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ProjectName = Column(String)
    DepartmentID = Column(Integer, default=0)
    LeaderID = Column(Integer)
    ProductID = Column(Integer)
    State = Column(Integer)
    ZTID = Column(Integer)
    CreateDate = Column(DateTime)
    CreateUser = Column(Integer)
    UpdateDate = Column(DateTime)
    UpdateUser = Column(Integer)
    Type = Column(SmallInteger, default=0)

    def __init__(self, fields: dict):
        self.ID = fields.get('ID')
        self.ProjectName = fields.get('ProjectName')
        self.DepartmentID = fields.get('DepartmentID')
        self.LeaderID = fields.get('LeaderID')
        self.ProductID = fields.get('ProductID')
        self.State = fields.get('State')
        self.ZTID = fields.get('ZTID')
        self.CreateDate = fields.get('CreateDate')
        self.CreateUser = fields.get('CreateUser')
        self.CreateUser = fields.get('CreateUser')
        self.UpdateDate = fields.get('UpdateDate')
        self.UpdateUser = fields.get('UpdateUser')
        self.Type = fields.get('Type')

    @classmethod
    def query_project(cls, condition: dict):
        try:
            result = session.query(cls)
            if condition.get('ZTID'):
                result = result.filter(cls.ZTID == condition.get('ZTID'))
            if condition.get('ProjectName'):
                result = result.filter(cls.ProjectName == condition.get('ProjectName'))
            # return result.all()
            return result.first()
        except Exception as e:
            print(str(e))
        finally:
            session.close()

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# 任务
class WeeklyTask(Base):
    __tablename__ = 'T_WeeklyTask'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    WeeklyID = Column(Integer)
    Name = Column(String)
    # DeadLine
    TaskType = Column(String)
    # Level
    ZTID = Column(String, default=0)
    ProjectSummaryID = Column(Integer)
    TaskDescrible = Column(String)
    ActualStartDate = Column(DateTime)
    ActualDeadLine = Column(DateTime)
    TaskStatus = Column(String)  # 枚举值 1-未开始,2-进行中,3-已暂停,4-已完成,5-已取消
    DutyUserID = Column(Integer)  # Owner
    RelateTestBill = Column(String)  # 测试单ID
    RelateReport = Column(String)  # 相关报告
    AddUserID = Column(Integer)
    # WeeklyTaskID
    IsDelete = Column(Integer, default=0)

    def __init__(self, fields: dict):
        # self.ID = fields.get('ID')
        self.WeeklyID = fields.get('WeeklyID')
        self.Name = fields.get('Name')
        self.TaskType = fields.get('TaskType')
        self.ZTID = fields.get('ZTID')
        self.ProjectSummaryID = fields.get('ProjectSummaryID')
        self.TaskDescrible = fields.get('TaskDescrible')
        self.ActualStartDate = fields.get('ActualStartDate')
        self.ActualDeadLine = fields.get('ActualDeadLine')
        self.TaskStatus = fields.get('TaskStatus')
        self.DutyUserID = fields.get('DutyUserID')
        self.RelateTestBill = fields.get('RelateTestBill')
        self.RelateReport = fields.get('RelateReport')
        self.AddUserID = fields.get('AddUserID')

    @classmethod
    def query_wt(cls, condition: dict):
        try:
            result = session.query(cls)
            # if condition.get('ID'):
            #     result = result.filter(cls.ID == condition.get('ID'))
            # if condition.get('WeeklyID') and condition.get('WeeklyID') != 0:
            #     result = result.filter(cls.WeeklyID == condition.get('WeeklyID'))
            if condition.get('TaskType'):
                result = result.filter(cls.TaskType == condition.get('TaskType'))
            if condition.get('ZTID'):
                result = result.filter(cls.ZTID == condition.get('ZTID'))
            return result.first()
        except Exception as e:
            print("query_wt异常：" + str(e))
        finally:
            session.close()

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# 周报
class WeeklyReportModel(Base):
    __tablename__ = 'T_WeeklyReport'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    WeeklyDate = Column(String)
    ReportUserID = Column(Integer)
    State = Column(Integer)
    WeeklyState = Column(Integer)
    CreateDate = Column(DateTime)
    CreateUser = Column(Integer)
    UpdateDate = Column(DateTime)
    UpdateUser = Column(Integer)

    def __init__(self, fields: dict):
        # self.ID = fields.get('ID')
        self.WeeklyDate = fields.get('WeeklyDate')
        self.ReportUserID = fields.get('ReportUserID')
        self.State = fields.get('State')
        self.ZTID = fields.get('ZTID')
        self.WeeklyState = fields.get('WeeklyState')
        self.CreateDate = fields.get('CreateDate')
        self.CreateUser = fields.get('CreateUser')
        self.UpdateDate = fields.get('UpdateDate')
        self.UpdateUser = fields.get('UpdateUser')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


if __name__ == "__main__":
    # wps = WeeklyProjectSummary()
    # print(query_by_primary_key(21338, WeeklyProjectSummary))

    pd = {
        'ID': 59,
        'ProjectName': '测试项目',
        'DepartmentID': 0,
        'LeaderID': 114,
        'ProductID': 1030,
        'State': 1,
        'ZTID': 1,
        # 'CreateDate': datetime.datetime.now(),
        'CreateUser': 114,
        # 'UpdateDate': datetime.datetime.now(),
        'UpdateUser': 114,
        'Type': 0
    }

    pj = Project(pd)
    update_column(pd, Project)
