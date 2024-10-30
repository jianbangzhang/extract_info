# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : transform_md.py
# Time       ：2024/10/22 13:57
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
from natsort import natsorted


class MarkdownConverter:
    def __init__(self):
        self.description="此类用于转markdown数据格式..."


    def is_title(self, line):
        """
        :param line:
        :return:
        """
        line = line.strip()

        if line[0] in "一二三四五六七八九十123456789" and all(
            [False if token in line else True for token in "<>()（）"]
        ):
            if len(line) < 20:
                return True
        return False

    def convert_line_to_markdown(self, line):
        """
        :param line:
        :return:
        """
        line = line.strip()

        if line and self.is_title(line):
            if line[0] in "一二三四五六七八九十":
                header_level = 1
            elif '.' in line:
                header_level = line.count('.') + 1
            else:
                header_level = 2
            return f"{'#' * header_level} {line}"
        else:
            return line

    def convert_to_markdown(self, lines):
        """
        :param lines:
        :return:
        """
        content_list = []
        for line in lines.split("\n"):
            markdown_line = self.convert_line_to_markdown(line)
            content_list.append(markdown_line)

        return "\n".join(content_list)

    def read_txt_file(self, file_path):
        """
        :param file_path:
        :return:
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def read_md_file(self, file_path):
        """
        :param file_path:
        :return:
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def save_to_md(self, data, output_md_path):
        """
        :param data:
        :param output_md_path:
        :return:
        """
        os.makedirs(os.path.dirname(output_md_path),exist_ok=True)
        with open(output_md_path, 'w', encoding='utf-8') as file:
            file.write(data)

    def combine_many_md(self, md_dir, output_md_path):
        """
        :param md_dir:
        :param output_md_path:
        :return:
        """
        os.makedirs(os.path.dirname(output_md_path),exist_ok=True)
        combined_content = []
        md_files=natsorted(os.listdir(md_dir))
        for file in md_files:
            file_path=os.path.join(md_dir,file)
            if os.path.isfile(file_path) and file_path.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    combined_content.append(file.read())
        combined_markdown = "\n".join(combined_content)
        self.save_to_md(combined_markdown, output_md_path)


