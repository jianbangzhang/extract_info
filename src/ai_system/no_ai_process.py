# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : no_ai_process.py
# Time       ：2024/10/9 11:33
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""


class NoAIProcesser(object):
    def __init__(self,config):
        self.config=config

    def run_api(self,file_path,doc_name):
        """
        :param file_path:
        :param doc_name:
        :return:
        """
        total_content=[]
        page_text={}
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            page_text[doc_name]=file_path
            total_content.append(page_text)
        elif file_path.endswith('.csv'):
            page_text[doc_name] = file_path
            total_content.append(page_text)
        elif file_path.endswith('.txt'):
            page_text[doc_name] = file_path
            total_content.append(page_text)
        else:
            page_text[doc_name] = file_path
            total_content.append(page_text)
        return total_content

