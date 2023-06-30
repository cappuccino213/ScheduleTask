# ScheduleTask
## 技术架构
- 基于数据采集使用SqlAlchemy数据查询+API调用的方式，定时任务使用apscheduler定时任务框架

## 项目结构简要说明
- database_model.py: 数据库链接创建使用ORM模式（sqlalchemy）
- schedule_*.py: 各定时任务业务实现模块
- schedule_execute.py: 定时任务执行模块
