# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : set_config.py
# Time       ：2024/10/7 09:10
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
import shutil



class Config(object):
    def __init__(self):
        self.config = {}
        self.dir = []
        self.file = []

    def __call__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
            self.config[key] = value
            if "dir" in key:
                self.dir.append(value)
            if ".txt" in str(value) or ".json" in str(value):
                self.file.append(value)

        if self.config.get("check_and_clean", False):
            print("正在初始化...")
            self._init_clean_dir()
            self._init_make_file()
        else:
            print("Warnings:未开启初始化...")
            self._init_make_file()

    def _init_clean_dir(self):
        for dir_path in self.dir:
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    try:
                        if filename.startswith('.'):
                            print(f"Removing hidden file: {file_path}")
                            os.unlink(file_path)
                        elif os.path.isfile(file_path):
                            os.unlink(file_path)
                            print(f"Removed file: {file_path}")
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            print(f"Removed directory: {file_path}")
                        else:
                            continue
                    except Exception as e:
                        print(f"Error removing {file_path}: {e}")
            else:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Directory {dir_path} does not exist, no need to clean and create Directory of {dir_path}.")

    def _init_make_file(self):
        for file_path in self.file:
            if ".txt" in str(file_path) or ".json" in str(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding="utf-8") as f:
                    f.write("")
                print(f"File {file_path} has been created.")
            else:
                continue



