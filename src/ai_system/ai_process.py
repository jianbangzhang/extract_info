# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : ai_process.py
# Time       ：2024/10/9 11:18
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
from .vqa import VQAApi
from .ocr import OCRApi
from .page_layout import LayoutAnalyzer
from natsort import natsorted




class AIProcessor:
    def __init__(self, config):
        """
        :param config: 
        """
        self.config = config
        self.layerout_analyzer=LayoutAnalyzer()
        self.vqa_output_dir=config.vqa_output_dir
        self.ocr_model_url=config.ocr_model_url
        self.ppt_prompt=config.ppt_prompt
        self.ocr_output_dir=config.ocr_result_dir
        self.process_image_schema=config.process_image_schema
        self._init_model()

    def _init_model(self):
        self.vqa_api=VQAApi(self.config)
        self.ocr_api=OCRApi(self.config)

    def run_ai(self, input_data_path,process_result_dir,document_name, task="ocr"):
        """
        :param input_data_path: 
        :param process_result_dir: 
        :param document_name: 
        :param task: 
        :return: 
        """
        os.makedirs(self.ocr_output_dir, exist_ok=True)
        if not os.path.exists(input_data_path):
            raise FileNotFoundError(f"The specified input data path does not exist: {input_data_path}")

        if task == "ocr":
            text_page=self.ocr_api.get_ocr_result(self.ocr_model_url, input_data_path, self.ocr_output_dir,process_result_dir,document_name)

        elif task == "vqa":
            text_page=self.vqa_api.get_vqa_result(self.ppt_prompt, input_data_path, self.vqa_output_dir,process_result_dir,document_name)

        else:
            raise NotImplementedError(f"The specified task '{task}' is not implemented.")
        return text_page

    def _vqa_ocr_combine_one_image(self,process_result_dir,image_file,zipfile,data_dict):
        """
        :param process_result_dir: 
        :param image_file: 
        :param zipfile: 
        :param data_dict: 
        :return: 
        """
        text_page=[]
        document_name=data_dict["file"]
        content_dict_lst=self.ocr_api.get_ocr_one_page_result(self.ocr_model_url, zipfile, self.ocr_output_dir,process_result_dir,document_name)
        if not content_dict_lst:
            return text_page
        self.layerout_analyzer.set_document_text(content_dict_lst[0]["image"])
        is_complex=self.layerout_analyzer.is_page_layout_complex()
        if is_complex:
            data_dict["task"]="vqa"
            text_page=self.vqa_api.get_vqa_result(self.ppt_prompt, image_file, self.vqa_output_dir,process_result_dir,document_name)
        else:
            data_dict["task"]="ocr"
            text_page=self.ocr_api.get_ocr_result(self.ocr_model_url, zipfile, self.ocr_output_dir,process_result_dir,document_name,ocr_before=True,ocr_result=content_dict_lst)
        return text_page

    def vqa_ocr_combine(self,process_result_dir,data_dict):
        """
        :param process_result_dir: 
        :param data_dict: 
        :return: 
        """
        total_pages=[]
        image_dir=data_dict["images"]
        zip_dir=data_dict["zip"]
        image_files=[os.path.join(image_dir,file) for file in natsorted(os.listdir(image_dir)) if file.endswith(".png")]
        zip_files=[os.path.join(zip_dir,file) for file in natsorted(os.listdir(zip_dir)) if file.endswith(".zip")]

        for image_file,zipfile in zip(image_files,zip_files):
            text_page=self._vqa_ocr_combine_one_image(process_result_dir,image_file,zipfile,data_dict)
            total_pages+=text_page
        return total_pages
