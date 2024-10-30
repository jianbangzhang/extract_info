# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : read_files.py
# Time       ：2024/10/7 08:41
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
from .convert_doc import DocumentConverter


class DirectoryTraverser:
    def __init__(self, config):
        """
        :param config:
        """
        self.file_path = config.file_path
        self.output_file = config.path_file
        self.project_path = config.project_path
        self.raw_doc_dir = config.raw_doc_dir
        self.raw_video_dir= config.raw_video_dir
        self.max_depth = self.get_max_depth()
        self.convert_doc = DocumentConverter()
        self.max_thread = config.max_thread
        self.set_runtime = config.set_runtime
        self.timeout= config.task_timeout

    def get_max_depth(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The path {self.file_path} does not exist.")
        if not os.path.isdir(self.file_path):
            raise NotADirectoryError(f"The path {self.file_path} is not a directory.")

        max_depth = 0
        for root, dirs, files in os.walk(self.file_path):
            depth = root.count(os.sep)
            if depth > max_depth:
                max_depth = depth
        return max_depth

    def convert_doc_process(self, root, file):
        """
        :param root:
        :param file:
        :return:
        """
        try:
            file_name = file.replace(".doc", "")
            pdf_file_path = os.path.join(self.project_path, root, file_name + ".pdf")
            doc_file_path = os.path.join(self.project_path, root, file)
            self.convert_doc.doc_to_pdf(doc_file_path, pdf_file_path, self.raw_doc_dir)
            return file_name + ".pdf"
        except Exception as e:
            print(f"Error converting {file} to PDF: {e}")
            return file

    def convert_video_process(self, root, file):
        """
        :param root:
        :param file:
        :return:
        """
        try:
            file_name,_ = os.path.splitext(file)
            audio_file_path = os.path.join(self.project_path, root, file_name + ".wav")
            video_file_path = os.path.join(self.project_path, root, file)
            self.convert_doc.extract_audio_from_video(video_file_path, audio_file_path, self.raw_video_dir)
            return file_name + ".wav"
        except Exception as e:
            print(f"Error converting {file} to PDF: {e}")
            return file

    def process_file(self, root, file):
        """
        :param root:
        :param file:
        :return:
        """
        if file.endswith(".doc"):
            file = self.convert_doc_process(root, file)

        if file.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpeg", ".mpg")):
            file = self.convert_video_process(root,file)

        file_path = os.path.join(self.project_path, root, file)
        file_name,_=os.path.splitext(file)
        return file_name, file_path


    def traverse_directory(self):
        if os.path.exists(self.output_file):
            print("Delete file before getting paths")
            os.remove(self.output_file)

        with open(self.output_file, 'a', encoding='utf-8') as f:
                for root, dirs, files in os.walk(self.file_path):
                    if str(dirs).startswith("_"):
                        continue
                    depth = root.count(os.sep)
                    if depth <= self.max_depth:
                        for file in files:
                            if file.startswith("."):
                                continue
                            file, file_path=self.process_file(root, file)
                            f.write(f"{file}\t\t{file_path}\n")
                            print(f"路径: {file_path}")


    def traverse_directory_with_accelerate(self):
        max_workers = min(cpu_count(),self.max_thread)
        if os.path.exists(self.output_file):
            print("Delete file before getting paths")
            os.remove(self.output_file)

        with open(self.output_file, 'a', encoding='utf-8') as f:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for root, dirs, files in os.walk(self.file_path):
                    if str(dirs).startswith("__"):
                        continue
                    depth = root.count(os.sep)
                    if depth <= self.max_depth:
                        for file in files:
                            if file.startswith("."):
                                continue
                            futures.append(executor.submit(self.process_file, root, file))

                for future in as_completed(futures):
                    try:
                        if self.set_runtime:
                            file, file_path = future.result(timeout=self.timeout)
                        else:
                            file, file_path = future.result()
                        f.write(f"{file}\t\t{file_path}\n")
                        print(f"路径: {file_path}")
                    except Exception as e:
                        print(f"Error processing file: {e}")



