# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : transform_result.py
# Time       ：2024/10/8 14:25
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
from .transform_md import MarkdownConverter
from utils import copy_file
from natsort import natsorted




class ProcessResultAPI(object):
    def __init__(self,config):
        """
        :param config:
        """
        self.clean_file_dir = config.clean_text_result_dir
        self.final_md_dir = config.final_result_dir
        self.md_converter = MarkdownConverter()
        self.schema = config.schema
        self.ppt_ocr_vqa_option = config.ppt_ocr_vqa_option

    def copy_md_file(self, file_path, doc_name):
        """
        :param file_path:
        :param doc_name:
        :return:
        """
        final_path = os.path.join(self.final_md_dir,doc_name, os.path.basename(file_path))
        os.makedirs(os.path.dirname(final_path),exist_ok=True)
        copy_file(file_path, final_path)


    def convert_conbine_md(self,ocr_file,vqa_file, doc_name):
        ocr_txt_content = self.md_converter.read_txt_file(ocr_file)
        if "document" in ocr_txt_content and "version" in ocr_txt_content and "image" in ocr_txt_content:
            md_lst=[]
            try:
                content_lst = eval(ocr_txt_content)
            except:
                content_lst = ocr_txt_content

            for data_dict in content_lst:
                doc_lst = data_dict["document"]
                for dic in doc_lst:
                    content = dic["value"]
                    md_lst.append(content)
            ocr_txt_content = "\n".join(md_lst)
        else:
            ocr_txt_content=ocr_txt_content
        vqa_txt_content = self.md_converter.read_txt_file(vqa_file)
        ocr_markdown_content = self.md_converter.convert_to_markdown(ocr_txt_content)
        vqa_markdown_content = self.md_converter.convert_to_markdown(vqa_txt_content)
        total_markdown_content = "# OCR:\n"+ocr_markdown_content+"\n"+"# VQA:\n"+vqa_markdown_content
        final_md_path = os.path.join(self.final_md_dir, doc_name, f"{os.path.splitext(os.path.basename(ocr_file))[0]}.md")
        self.md_converter.save_to_md(total_markdown_content, final_md_path)

    def convert_txt_to_md(self, file_path,doc_name):
        """
        :param file_path:
        :param doc_name:
        :return:
        """
        txt_content = self.md_converter.read_txt_file(file_path)
        if "document" in txt_content and "version" in txt_content and "image" in txt_content:
            md_lst=[]
            try:
                content_lst = eval(txt_content)
            except:
                content_lst = txt_content

            for data_dict in content_lst:
                doc_lst = data_dict["document"]
                for dic in doc_lst:
                    content = dic["value"]
                    md_lst.append(content)
            txt_content = "\n".join(md_lst)
        else:
            txt_content=txt_content
        markdown_content = self.md_converter.convert_to_markdown(txt_content)
        final_md_path = os.path.join(self.final_md_dir, doc_name, f"{os.path.splitext(os.path.basename(file_path))[0]}.md")
        self.md_converter.save_to_md(markdown_content, final_md_path)

    def combine_txt_md_file(self,txt_file,md_file,doc_name):
        """
        :param txt_file:
        :param md_file:
        :param doc_name:
        :return:
        """
        txt_content = self.md_converter.read_txt_file(txt_file)
        txt_markdown_content = self.md_converter.convert_to_markdown(txt_content)
        md_markdown_content = self.md_converter.read_md_file(md_file)
        if md_markdown_content:
            total_markdown_content = md_markdown_content+"\n"+"*"*80+"\n"+txt_markdown_content
        else:
            total_markdown_content = txt_markdown_content
        final_md_path = os.path.join(self.final_md_dir, doc_name, f"{os.path.splitext(os.path.basename(md_file))[0]}.md")
        self.md_converter.save_to_md(total_markdown_content, final_md_path)


    def combine_md_files(self,doc_name):
        """
        :param doc_name:
        :return:
        """
        md_dir = os.path.join(self.final_md_dir,doc_name)
        output_md_path = os.path.join(self.final_md_dir,doc_name,"merge","total.md")
        self.md_converter.combine_many_md(md_dir, output_md_path)

    def _handle_files(self,file_path,doc_name):
        file_list = natsorted(
            [os.path.join(file_path, file_name) for file_name in os.listdir(file_path) if
             file_name.endswith((".txt", ".md"))])
        txt_lst = natsorted([txt_file for txt_file in file_list if txt_file.endswith(".txt")])
        md_lst = natsorted([md_file for md_file in file_list if md_file.endswith(".md")])
        page_num = max(len(txt_lst), len(md_lst))
        for page_id in range(page_num):
            if txt_lst and not md_lst:
                txt_file = txt_lst[page_id]
                self.convert_txt_to_md(txt_file, doc_name)
            elif not txt_lst and md_lst:
                md_file = md_lst[page_id]
                self.copy_md_file(md_file, doc_name)
            elif txt_lst and md_lst:
                txt_name = str(page_id) + ".txt"
                md_name = str(page_id) + ".md"
                txt_file = os.path.join(file_path, txt_name)
                md_file = os.path.join(file_path, md_name)
                self.combine_txt_md_file(txt_file, md_file, doc_name)
            else:
                continue

    def process_files(self):
        if not os.path.exists(self.final_md_dir):
            os.makedirs(self.final_md_dir)

        doc_list = [f for f in os.listdir(self.clean_file_dir) if not f.startswith(".")]
        for doc_name in doc_list:
            doc_file_path = os.path.join(self.clean_file_dir, doc_name)

            if self.ppt_ocr_vqa_option and self.schema=="part":
                self._handle_files(doc_file_path,doc_name)

            elif self.ppt_ocr_vqa_option and self.schema=="all":
                doc_ocr_dir = os.path.join(doc_file_path,"ocr_result")
                doc_vqa_dir = os.path.join(doc_file_path, "vqa_result")

                if not os.path.exists(doc_ocr_dir) and not os.path.exists(doc_ocr_dir):
                    self._handle_files(doc_file_path,doc_name)
                else:
                    ocr_file_list = natsorted(
                        [os.path.join(doc_ocr_dir, file_name) for file_name in os.listdir(doc_ocr_dir) if file_name.endswith(".txt")])
                    vqa_file_list = natsorted(
                        [os.path.join(doc_vqa_dir, file_name) for file_name in os.listdir(doc_vqa_dir) if file_name.endswith(".txt")])

                    page_num = max(len(ocr_file_list), len(vqa_file_list))
                    for page_id in range(page_num):
                        try:
                            page_name=f"{page_id}.txt"
                            is_in_ocr = any([True if page_name == f else False for f in os.listdir(doc_ocr_dir)])
                            is_in_vqa = any([True if page_name == f else False for f in os.listdir(doc_vqa_dir)])
                            if is_in_vqa and not is_in_ocr:
                                vqa_file=os.path.join(doc_vqa_dir,page_name)
                                self.convert_txt_to_md(vqa_file,doc_name)
                            elif not is_in_vqa and is_in_ocr:
                                ocr_file = os.path.join(doc_ocr_dir, page_name)
                                self.convert_txt_to_md(ocr_file, doc_name)
                            elif is_in_vqa and is_in_ocr:
                                vqa_file = os.path.join(doc_vqa_dir, page_name)
                                ocr_file = os.path.join(doc_ocr_dir, page_name)
                                self.convert_conbine_md(ocr_file,vqa_file, doc_name)
                            else:
                                continue
                        except:
                            continue
            else:
                file_list = natsorted(
                    [os.path.join(doc_file_path, file_name) for file_name in os.listdir(doc_file_path) if
                     file_name.endswith((".txt", ".md"))])
                for file_path in file_list:
                    file_name_with_extension = os.path.basename(file_path)
                    if os.path.isfile(file_path):
                        if file_name_with_extension.endswith('.md'):
                            self.copy_md_file(file_path, doc_name)
                        elif file_name_with_extension.endswith('.txt'):
                            self.convert_txt_to_md(file_path, doc_name)


        final_doc_list = [doc for doc in os.listdir(self.final_md_dir) if not doc.startswith(".")]
        for doc_name in final_doc_list:
            doc_file_path = os.path.join(self.final_md_dir, doc_name)
            os.makedirs(doc_file_path,exist_ok=True)
            file_list = natsorted([os.path.join(doc_file_path, file_name) for file_name in os.listdir(doc_file_path) if
                         file_name.endswith(".md")])
            if len(file_list) > 1:
                self.combine_md_files(doc_name)
            else:
                continue
        print("数据处理完成！")




