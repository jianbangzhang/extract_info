# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : refine_result.py
# Time       ：2024/10/9 15:59
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
import shutil
from utils import read_json_file,read_txt_file,find_result_name


class RefineResult(object):
    def __init__(self, config):
        """
        :param config:
        """
        self.config = config
        self.json_result_dir=config.json_result_dir
        self.process_result_dir = config.process_result_dir
        self.clean_text_result_dir=config.clean_text_result_dir
        self.schema = config.schema
        self.process_image_schema=config.process_image_schema
        self.ppt_ocr_vqa_option = config.ppt_ocr_vqa_option

    def is_path_like(self,path_str):
        """
        :param path_str: 要检查的字符串
        :return: 如果字符串看起来像路径，返回True；否则返回False
        """
        if not path_str:
            return False

        if os.path.isabs(path_str):
            return True

        if any(sep in path_str for sep in (os.sep, os.altsep)):
            return True

        if os.path.splitext(path_str)[1]:
            return True

        return False

    def copy_file(self,source_path, destination_path):
        """
        :param source_path:
        :param destination_path:
        :return:
        """
        dir_name = os.path.dirname(destination_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        try:
            shutil.copy(source_path, destination_path)
            return "文件复制成功！"
        except Exception as e:
            return f"复制文件时出错：{e}"


    def write_to_txt(self,text, out_path):
        """
        :param text:
        :param out_path:
        :return:
        """
        with open(out_path, "w", encoding="utf-8") as txt_file:
            for line in text.split("\n"):
                txt_file.write(line + "\n")

        print(f"成功写入:{out_path}")

    def write_to_markdown(self,contents, file_path):
        """
        :param contents:
        :param file_path:
        :return:
        """
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(contents)

        return f"Content written to {file_path}"


    def save_to_md(self,data_path,doc_name,file_name):
        """
        :param data_path:
        :param doc_name:
        :param file_name:
        :return:
        """
        md_lst = []
        content_lst=read_txt_file(data_path)
        try:
            content_lst=eval(content_lst)
        except:
            content_lst=content_lst

        for data_dict in content_lst:
            doc_lst = data_dict["document"]
            for dic in doc_lst:
                content = dic["value"]
                md_lst.append(content)
        md_content = "\n".join(md_lst)
        output_md_path = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.md")
        os.makedirs(os.path.dirname(output_md_path),exist_ok=True)
        self.write_to_markdown(md_content, output_md_path)

    def process_result_files(self):
        json_file_lst=[f for f in os.listdir(self.json_result_dir) if f.endswith(".json")]
        for file in json_file_lst:
            print(f"正在处理{file}...")
            file_path=os.path.join(self.json_result_dir,file)
            data_dict=read_json_file(file_path)

            if self.schema=="zero":
                self._process_zero_schema(data_dict)
            elif self.schema=="all":
                self._process_all_schema(data_dict)
            elif self.schema=="part":
                self._process_part_schema(data_dict)
            else:
                raise NotImplementedError


    def _process_zero_schema(self,data_dict):
        """
        :param data_dict:
        :return:
        """
        task = data_dict["task"]
        doc_name = data_dict["file"]
        result_name = find_result_name(data_dict)
        res_file_lst = data_dict[result_name]

        if data_dict["type"] in ["image", "video", "audio"]:
            if task == "ocr" or task == "vqa":
                if res_file_lst:
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        if os.path.exists(res_path):
                            self.save_to_md(res_path, doc_name, file_name)
                        else:
                            continue
            else:
                raise ValueError
        else:
            if task == "no_ai":
                for file_dict in res_file_lst:
                    file_name, res_path = list(*file_dict.items())
                    if ".txt" in res_path:
                        out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                        self.copy_file(res_path, out_txt_file)
                    elif ".md" in res_path:
                        out_md_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.md")
                        self.copy_file(res_path, out_md_file)
            else:
                raise ValueError

    def _handle_files(self,doc_name,res_file_list,result_name_list,key_word):
        result_file_lst = res_file_list[result_name_list.index(key_word)]
        for file_dict in result_file_lst:
            lst = list(*file_dict.items())
            if not lst:
                continue
            file_name, res_path = lst
            out_md_file = os.path.join(self.clean_text_result_dir, doc_name, key_word, os.path.basename(res_path))
            self.copy_file(res_path, out_md_file)

    def _process_all_schema(self,data_dict):
        """
        :param data_dict:
        :return:
        """
        task = data_dict["task"]
        doc_name = data_dict["file"]
        result_name_list = find_result_name(data_dict)
        res_file_list = [data_dict[result_name] for result_name in result_name_list]

        res_file_lst=res_file_list[0]
        if data_dict["type"] in ["docx","pdf","pptx","image", "video", "audio"]:
            if task == "ocr" or task == "vqa":
                if data_dict["type"]=="pptx" and self.ppt_ocr_vqa_option:
                    self._handle_files(doc_name,res_file_list,result_name_list,key_word="ocr_result")
                    self._handle_files(doc_name, res_file_list, result_name_list, key_word="vqa_result")
                else:
                    if res_file_lst:
                        try:
                            for file_dict in res_file_lst:
                                file_name, res_path = list(*file_dict.items())
                                self.save_to_md(res_path, doc_name, file_name)
                        except Exception as e:
                            print(str(e))
            else:
                raise ValueError
        else:
            if task == "no_ai":
                for file_dict in res_file_lst:
                    file_name, res_path = list(*file_dict.items())
                    if ".txt" in res_path:
                        out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                        self.copy_file(res_path, out_txt_file)
                    elif ".md" in res_path:
                        out_md_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.md")
                        self.copy_file(res_path, out_md_file)
            else:
                raise ValueError



    def _process_part_schema(self,data_dict):
        """
        :param data_dict:
        :return:
        """
        doc_name = data_dict["file"]
        result_name_list = find_result_name(data_dict)
        res_file_list = [data_dict[result_name] for result_name in result_name_list]
        task = data_dict["task"]

        res_file_lst=res_file_list[0]
        if self.process_image_schema=="mix":
            if data_dict["type"] in ["image", "video", "audio"]:
                if res_file_lst:
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        self.save_to_md(res_path, doc_name, file_name)

            elif data_dict["type"] in ["pdf", "docx", "pptx"]:
                if data_dict["type"]=="pptx" and self.ppt_ocr_vqa_option:
                    res_file_lst = res_file_list[0] + res_file_list[-1]
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        if ".txt" in res_path:
                            out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                            self.copy_file(res_path, out_txt_file)
                        elif ".md" in res_path:
                            out_md_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.md")
                            self.copy_file(res_path, out_md_file)
                else:
                    if res_file_lst:
                        for file_dict in res_file_lst:
                            file_name, res_path = list(*file_dict.items())
                            self.save_to_md(res_path, doc_name, file_name)

                text_dir = data_dict["text"]
                if text_dir:
                    txt_list = [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")]
                    for txt_file in txt_list:
                        file_name, _ = os.path.splitext(os.path.basename(txt_file))
                        out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                        self.copy_file(txt_file, out_txt_file)
            else:
                if task == "no_ai" and res_file_lst:
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        if ".txt" in res_path:
                            out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                            self.copy_file(res_path, out_txt_file)
                        elif ".md" in res_path:
                            out_md_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.md")
                            self.copy_file(res_path, out_md_file)
                else:
                    raise ValueError
        elif self.process_image_schema=="pure":
            if data_dict["type"] in ["image", "video", "audio"]:
                if res_file_lst:
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        self.save_to_md(res_path, doc_name, file_name)

            elif data_dict["type"] in ["pdf", "docx", "pptx"]:
                if res_file_lst:
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        self.save_to_md(res_path, doc_name, file_name)

                text_dir = data_dict["text"]
                if text_dir:
                    txt_list = [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")]
                    for txt_file in txt_list:
                        file_name, _ = os.path.splitext(os.path.basename(txt_file))
                        out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                        self.copy_file(txt_file, out_txt_file)

            else:
                if task == "no_ai" and res_file_lst:
                    for file_dict in res_file_lst:
                        file_name, res_path = list(*file_dict.items())
                        if ".txt" in res_path:
                            out_txt_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.txt")
                            self.copy_file(res_path, out_txt_file)
                        elif ".md" in res_path:
                            out_md_file = os.path.join(self.clean_text_result_dir, doc_name, f"{file_name}.md")
                            self.copy_file(res_path, out_md_file)
                else:
                    raise ValueError




