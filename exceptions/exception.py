# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : exception.py
# Time       ：2024/10/8 9:24
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""

class FileNotFoundError(Exception):
    def __init__(self, message="文件不存在"):
        self.message = message
        super().__init__(self.message)


class DirPathError(Exception):
    def __init__(self, message="文件夹路径错误"):
        self.message = message
        super().__init__(self.message)


class FilePathError(Exception):
    def __init__(self,message="文件路径错误"):
        self.message=message
        super().__init__(self.message)

class ConvertTOPdfError(Exception):
    def __init__(self,message="转化pdf失败"):
        self.message=message
        super(ConvertTOPdfError, self).__init__(self.message)


class ExtractAudioError(Exception):
    def __init__(self,message="提取音频错误"):
        self.message=message
        super(ExtractAudioError, self).__init__(self.message)






