# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : run_accelerate.py
# Time       ：2024/10/9 16:34
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
from config import FileConfig
from config import VQAConfig, OCRConfig
from config import ProjectConfig
from config import Config
from src.file_system import DirectoryTraverser
from src.file_system import FileChecker
from src.file_system import DocumentProcessor
from src.classify_system import ClassifyFiles
from src.ai_system import ProcessAPIWithAccelerate
from src.process_system import RefineResult
from src.save_system import ProcessResultAPI
from utils import compress_folder
import argparse


def getUserArgs():
    parser = argparse.ArgumentParser(description='The configure from users that set flexible variable.')
    parser.add_argument('--file_path', type=str, default="datasets/20241029170049/pptx1")
    parser.add_argument('--root_dir',type=str,default="mydata")
    args = parser.parse_args()
    return args



def combineArgs():
    user_args = getUserArgs()
    user_args_dict = vars(user_args)

    project_config = ProjectConfig()
    file_config = FileConfig(dataset_folder=user_args_dict["root_dir"])
    vqa_config = VQAConfig()
    ocr_config = OCRConfig()
    config = Config()

    project_config_dict = vars(project_config)
    file_config_dict = vars(file_config)
    vqa_config_dict = vars(vqa_config)
    ocr_config_dict = vars(ocr_config)

    total_config = {
        **project_config_dict,
        **file_config_dict,
        **vqa_config_dict,
        **ocr_config_dict,
        **user_args_dict
    }

    config(**total_config)
    return config


def process_pipeline_accelerated(config):
    """
    :param config:
    :return:
    """
    print("加速模式已启用")

    # 文件遍历
    print("1.开始遍历文件（加速版）...")
    traverser = DirectoryTraverser(config)
    traverser.traverse_directory_with_accelerate()
    print(f"遍历完成，结果已保存到 {traverser.output_file}")

    # 去重
    print("2.开始文档去重（加速版）...")
    file_checker = FileChecker(config)
    file_checker.find_duplicate_files_with_accelerate()

    # 降相似度
    print("3.降低文档相似度（加速版）...")
    file_processor = DocumentProcessor(config)
    file_processor.process_files_with_accelerate()

    # 文件读取分类
    print("4.文档处理分类（加速版）...")
    classify = ClassifyFiles(config)
    classify.handle_files_with_accelerate()

    # AI处理系统
    print("5.AI文档处理（加速版）...")
    process = ProcessAPIWithAccelerate(config)
    if config.process_file_parallel:
        process.process_task_with_accelerate()
    else:
        process.process_task()

    # 输出文档
    print("6.输出清洗文档结果（加速版）...")
    refine = RefineResult(config)
    refine.process_result_files()

    # 整理输出
    print("7.输出最终文档结果（加速版）...")
    process_result = ProcessResultAPI(config)
    process_result.process_files()
    print(f"结果保存在{config.final_result_dir}")

    # zip压缩
    print("8.正在压缩zip文件...")
    compress_folder(config.final_result_dir,config.zip_result_dir)
    zip_file = os.path.join(config.zip_result_dir , "result.zip")
    return zip_file





if __name__ == '__main__':
    total_config = combineArgs()
    zip_file=process_pipeline_accelerated(total_config)
    print(zip_file)
