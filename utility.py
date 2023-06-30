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
        return re.sub('[\n]+', '\n', txt_content)


if __name__ == "__main__":
    pass
