# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : file_config.py
# Time       ：2024/10/7 08:44
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os


class FileConfig(object):
    def __init__(self,dataset_folder=None):
        current_file_path = os.path.abspath('__file__')
        self.project_path = os.path.dirname(current_file_path)
        self.max_files_size=200
        self.zip_image_size = 1

        if dataset_folder is None:
            self.path_file="outputs/filePath/raw.txt"
            self.unique_file_path="outputs/filePath/unique.txt"
            self.input_data_path="outputs/filePath/input.json"
            self.duplicate_dir="outputs/duplicate_files"
            self.raw_doc_dir="outputs/raw_doc_files"
            self.raw_video_dir="outputs/raw_video_files"
            self.pptx_pdf_dir ="outputs/pptx_pdf"
            self.docx_pdf_dir = "outputs/docx_pdf"
            self.ocr_result_dir="outputs/ai_output/ocr"
            self.vqa_output_dir="outputs/ai_output/vqa"
            self.text_content_dir="outputs/input_data/text"
            self.mix_data_dir="outputs/ai_output/mix"
            self.tmp_data_dir = "outputs/temp"
            self.word_img_dir="outputs/input_data/images/word_image"
            self.single_img_dir="outputs/input_data/images/other_image"
            self.doc_zip_dir="outputs/input_data/images/zip_file/doc_zip"
            self.single_zip_dir="outputs/input_data/images/zip_file/single_zip"
            self.excel_dir="outputs/input_data/excel"
            self.audio_dir="outputs/input_data/audio"
            self.video_dir="outputs/input_data/video"
            self.process_result_dir="outputs/ai_output/result"
            self.final_result_dir="outputs/ai_output/final"
            self.clean_text_result_dir = "outputs/ai_output/clean"
            self.json_result_dir="outputs/ai_output/json"
            self.zip_result_dir="outputs/ai_output/zip"
        else:
            self.path_file = os.path.join(dataset_folder,"outputs/filePath/raw.txt")
            self.unique_file_path = os.path.join(dataset_folder,"outputs/filePath/unique.txt")
            self.input_data_path = os.path.join(dataset_folder,"outputs/filePath/input.json")
            self.duplicate_dir = os.path.join(dataset_folder,"outputs/duplicate_files")
            self.raw_doc_dir = os.path.join(dataset_folder,"outputs/raw_doc_files")
            self.raw_video_dir = os.path.join(dataset_folder,"outputs/raw_video_files")
            self.pptx_pdf_dir = os.path.join(dataset_folder,"outputs/pptx_pdf")
            self.docx_pdf_dir = os.path.join(dataset_folder,"outputs/docx_pdf")
            self.ocr_result_dir = os.path.join(dataset_folder,"outputs/ai_output/ocr")
            self.vqa_output_dir = os.path.join(dataset_folder,"outputs/ai_output/vqa")
            self.text_content_dir = os.path.join(dataset_folder,"outputs/input_data/text")
            self.mix_data_dir = os.path.join(dataset_folder,"outputs/ai_output/mix")
            self.tmp_data_dir = os.path.join(dataset_folder,"outputs/temp")
            self.word_img_dir = os.path.join(dataset_folder,"outputs/input_data/images/word_image")
            self.single_img_dir = os.path.join(dataset_folder,"outputs/input_data/images/other_image")
            self.doc_zip_dir = os.path.join(dataset_folder,"outputs/input_data/images/zip_file/doc_zip")
            self.single_zip_dir = os.path.join(dataset_folder,"outputs/input_data/images/zip_file/single_zip")
            self.excel_dir = os.path.join(dataset_folder,"outputs/input_data/excel")
            self.audio_dir = os.path.join(dataset_folder,"outputs/input_data/audio")
            self.video_dir = os.path.join(dataset_folder,"outputs/input_data/video")
            self.process_result_dir = os.path.join(dataset_folder,"outputs/ai_output/result")
            self.final_result_dir = os.path.join(dataset_folder,"outputs/ai_output/final")
            self.clean_text_result_dir = os.path.join(dataset_folder,"outputs/ai_output/clean")
            self.json_result_dir = os.path.join(dataset_folder,"outputs/ai_output/json")
            self.zip_result_dir = os.path.join(dataset_folder,"outputs/ai_output/zip")





