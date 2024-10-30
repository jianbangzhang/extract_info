# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : check_duplicates.py
# Time       ：2024/10/7 09:44
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
import hashlib
import shutil
from utils import read_files
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed



class FileChecker(object):
    def __init__(self, config):
        """
        :param config:
        """
        self.files_list = read_files(config.path_file)
        self.duplicate_directory = config.duplicate_dir
        self.max_thread=config.max_thread
        self.md5_dict = {}
        self.set_runtime = config.set_runtime
        self.timeout = config.task_timeout

        if not os.path.exists(self.duplicate_directory):
            os.makedirs(self.duplicate_directory)


    def calculate_md5(self, file_path):
        """
        :param file_path:
        :return:
        """
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        return md5_hash.hexdigest()


    def get_result(self,duplicate_files):
        """
        :param duplicate_files:
        :return:
        """
        if duplicate_files:
            print(f"找到 {len(duplicate_files)} 个重复文件，已移动到 {self.duplicate_directory}。")
        else:
            print("未找到重复文件。")

    def process_file(self, file_path):
        """
        :param file_path: 文件路径
        :return: (是否重复, 文件路径)
        """
        file_md5 = self.calculate_md5(file_path)
        if not file_md5:
            return False, file_path

        if file_md5 in self.md5_dict:
            print(f"重复文件： {file_path}")
            file_name = os.path.basename(file_path)
            shutil.move(file_path, os.path.join(self.duplicate_directory, file_name))
            return True, file_path
        else:
            self.md5_dict[file_md5] = file_path
            return False, file_path


    def find_duplicate_files(self):
        duplicate_files = []
        for file_path in self.files_list:
            is_duplicate, file_path=self.process_file(file_path)
            if is_duplicate:
                duplicate_files.append(file_path)

        self.get_result(duplicate_files)
        return duplicate_files


    def find_duplicate_files_with_accelerate(self):
        """
        并行查找重复文件
        :param max_workers: 线程池中的最大工作线程数
        :return: 重复文件列表
        """
        duplicate_files = []
        max_workers= min(min((cpu_count() + len(self.files_list)) // 2, self.max_thread), len(self.files_list))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_file, file_path) for file_path in self.files_list]

            for future in as_completed(futures):
                try:
                    if self.set_runtime:
                        is_duplicate, file_path = future.result(timeout=self.timeout)
                    else:
                        is_duplicate, file_path = future.result()
                    if is_duplicate:
                        duplicate_files.append(file_path)
                except Exception as e:
                    print(f"处理文件时出错: {e}")

        self.get_result(duplicate_files)
        return duplicate_files



