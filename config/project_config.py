# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : project_config.py
# Time       ：2024/10/10 14:51
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""

class ProjectConfig(object):
    def __init__(self):
        self.schema = "all"  # all part zero
        self.process_image_schema = "pure"  # pure mix
        self.check_and_clean = True
        self.is_retry = True
        self.max_retry_time = 2 # 2 * max_retry_time
        self.sleep_seconds = 0.001
        self.accelerate = True
        self.max_thread = 36
        self.ppt_ocr_vqa_option = True # True pptx ocr+vqa False pptx vqa
        self.vqa_request_parallel= True
        self.ocr_request_parallel = True
        self.process_file_parallel = False
        self.set_runtime = False
        self.task_timeout = 30
        self.mode = True

