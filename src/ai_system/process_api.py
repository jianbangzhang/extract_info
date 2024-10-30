# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : process_api.py
# Time       ：2024/10/9 11:33
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
import json
from multiprocessing import cpu_count
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

from .ai_process import AIProcessor
from .no_ai_process import NoAIProcesser
from utils import save_result_to_json




class ProcessAPIWithAccelerate(object):
    def __init__(self, config):
        """
        :param config:
        """
        self.data_path = config.input_data_path
        self.data_path_info = self.read_path_info()
        self.ai_module = AIProcessor(config)
        self.no_ai_module = NoAIProcesser(config)
        self.process_result_dir = config.process_result_dir
        self.schema = config.schema
        self.process_image_schema = config.process_image_schema
        self.json_result_dir = config.json_result_dir
        self.max_thread = config.max_thread
        self.ppt_ocr_vqa_option = config.ppt_ocr_vqa_option
        self.timeout = config.task_timeout
        self.set_runtime = config.set_runtime

    def read_path_info(self):
        with open(self.data_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    def _process_no_ai(self, data_dict):
        task = "no_ai"
        data_dict["task"] = task
        file_path = data_dict.get("text", data_dict["path"])
        doc_name = data_dict["file"]

        if data_dict["type"] != "excel":
            total_page = self.no_ai_module.run_api(file_path, doc_name)
            data_dict["result"] = total_page

    def _process_ocr_task(self, data_dict):
        task = "ocr"
        data_dict["task"] = task
        zip_file_dir = data_dict["zip"]
        file_name = data_dict["file"]
        total_page = self.ai_module.run_ai(zip_file_dir, self.process_result_dir, file_name, task)
        data_dict["ocr_result"] = total_page

    def _process_vqa_task(self, data_dict):
        task = "vqa"
        data_dict["task"] = task
        images_file_dir = data_dict["images"]
        file_name = data_dict["file"]
        total_page = self.ai_module.run_ai(images_file_dir, self.process_result_dir, file_name, task)
        data_dict["vqa_result"] = total_page

    def _process_image_task(self, data_dict):
        total_page = self.ai_module.vqa_ocr_combine(self.process_result_dir, data_dict)
        data_dict["vqa_ocr_result"] = total_page

    def _process_image_pipeline(self, data_dict):
        def run_tasks_in_parallel(data_dict):
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_ocr = executor.submit(self._process_ocr_task, data_dict)
                future_vqa = executor.submit(self._process_vqa_task, data_dict)

                ocr_result = future_ocr.result()
                vqa_result = future_vqa.result()
            return ocr_result, vqa_result

        file_name = data_dict["file"]
        json_path = os.path.join(self.json_result_dir, f"{file_name}.json")

        if data_dict["type"] == "pptx":
            if self.ppt_ocr_vqa_option:
                run_tasks_in_parallel(data_dict)
            else:
                self._process_vqa_task(data_dict)
        elif data_dict["type"] in ["pdf", "docx"] or ("zip" in data_dict and len(data_dict["zip"])) > 0:
            self._process_ocr_task(data_dict)
        else:
            self._process_no_ai(data_dict)

        save_result_to_json(data_dict, json_path)


    def _process_image_pipeline_no_parallel(self, data_dict):
        file_name = data_dict["file"]
        json_path = os.path.join(self.json_result_dir, f"{file_name}.json")

        if data_dict["type"] == "pptx":
            if self.ppt_ocr_vqa_option:
                self._process_ocr_task(data_dict)
                self._process_vqa_task(data_dict)
            else:
                self._process_vqa_task(data_dict)
        elif data_dict["type"] in ["pdf", "docx"] or ("zip" in data_dict and len(data_dict["zip"])) > 0:
            self._process_ocr_task(data_dict)
        else:
            self._process_no_ai(data_dict)
        save_result_to_json(data_dict, json_path)

    def _process_text_pipeline(self, data_dict):
        file_name = data_dict["file"]
        json_path = os.path.join(self.json_result_dir, f"{file_name}.json")

        if data_dict["type"] in ["image", "video", "audio"]:
            self._process_ocr_task(data_dict)
        else:
            self._process_no_ai(data_dict)  # "docx", "pdf", "pptx", "excel"

        save_result_to_json(data_dict, json_path)

    def _process_text_image_pipeline(self, data_dict):
        file_name = data_dict["file"]
        json_path = os.path.join(self.json_result_dir, f"{file_name}.json")

        if data_dict["type"] in ["image", "video", "audio"]:
            self._process_ocr_task(data_dict)
        elif data_dict["type"] in ["docx", "pdf", "pptx"]:
            image_pages = data_dict.get("image_page", [])
            if image_pages or self.process_image_schema == "pure":
                self._process_image_task(data_dict)
            else:
                self._process_no_ai(data_dict)
        else:
            self._process_no_ai(data_dict)
        save_result_to_json(data_dict, json_path)

    def _process_task_in_parallel(self, task_function):
        max_workers = min(min(cpu_count(), self.max_thread),len(self.data_path_info))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(task_function, data_dict): data_dict["file"] for data_dict in
                       self.data_path_info}
            for future in as_completed(futures):
                file_name = futures[future]
                try:
                    if self.set_runtime:
                        future.result(timeout=self.timeout)
                    else:
                        future.result()
                    print(f"Successfully processed file: {file_name}")
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")

    def process_task_with_accelerate(self):
        if self.schema == "all":
            self._process_task_in_parallel(self._process_image_pipeline)
        elif self.schema == "zero":
            self._process_task_in_parallel(self._process_text_pipeline)
        elif self.schema == "part":
            self._process_task_in_parallel(self._process_text_image_pipeline)
        else:
            raise ValueError("Unknown schema type")


    def process_task(self):
        for data_dict in self.data_path_info:
            if self.schema == "all":
                self._process_image_pipeline_no_parallel(data_dict)
            elif self.schema == "zero":
                self._process_text_pipeline(data_dict)
            elif self.schema == "part":
                self._process_text_image_pipeline(data_dict)
            else:
                raise ValueError("Unknown schema type")












