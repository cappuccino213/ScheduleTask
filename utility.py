"""
@File : utility.py
@Date : 2023/6/28 16:31
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import re
from bs4 import BeautifulSoup


# 工具类
class Toolkit:
    # 从html提取文本
    @staticmethod
    def parse_html(html_content):
        # bs = BeautifulSoup(open(r'C:\Users\eword\Desktop\不规范测试单内容.txt', 'r', encoding='utf-8'), 'html.parser')
        bs = BeautifulSoup(html_content, 'html.parser')
        # 按照换行符分割
        txt_content = bs.get_text(separator='\n')
        # 去空行
        txt = re.sub('[\n]+', '\n', txt_content)
        print(txt)
        return txt


if __name__ == "__main__":
#     Toolkit.parse_html("""<p><br /></p>
# <p>【New】</p>
# <p><br /></p>
# <ul>
#   <li>
#     <ul>
#       <li>新增Task插入自定义过滤条件</li>
#     </ul>
#     <ul>
#       <li><a href="/zentao/story-view-694.html">绍兴卫生局API需要同步更新1库 2库的miedia存储媒介</a></li>
#       <li><a href="/zentao/story-view-736.html">上传插件组 上传影像 无法便捷的分多组插件上传影像</a></li>
#       <li><a href="/zentao/story-view-737.html">采集TASK插入无法根据自定义需求来插入表，导致表内无效数据众多。</a></li>
#       <li><a href="/zentao/story-view-738.html">集成平台界面无法清晰的显示收费状态以及修改付费状态选项不明显</a></li>
#       <li><a href="/zentao/story-view-739.html">集成平台界面免密入参目前加密不安全，需要整改。</a><br /></li>
#     </ul>
#     <ul>
#       <li><a href="/zentao/story-view-751.html">集成平台支持通过patientid入参免密登录</a><br /></li>
#     </ul>
#   </li>
# </ul>
# <p>【Fix】</p>
# <ul>
#   <li>
#     <ul>
#       <li>&nbsp;</li>
#     </ul>
#   </li>
# </ul>
# <p>【update】</p>
# <p><br /></p>
# <p><br /></p>
# <p><br /></p>""")
    pass
