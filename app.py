# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : app.py
# Time       ：2024/10/7 08:45
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
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
import argparse


def getUserArgs():
    parser = argparse.ArgumentParser(description='The configure from users that set flexible variable.')
    parser.add_argument('--file_path', type=str, default="dataset/excel")
    args = parser.parse_args()
    return args



def combineArgs():
    user_args = getUserArgs()
    project_config = ProjectConfig()
    file_config = FileConfig()
    vqa_config = VQAConfig()
    ocr_config = OCRConfig()
    config = Config()

    project_config_dict = vars(project_config)
    file_config_dict = vars(file_config)
    vqa_config_dict = vars(vqa_config)
    ocr_config_dict = vars(ocr_config)

    user_args_dict = vars(user_args)

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
    traverser.traverse_directory()
    print(f"遍历完成，结果已保存到 {traverser.output_file}")

    # 去重
    print("2.开始文档去重（加速版）...")
    file_checker = FileChecker(config)
    file_checker.find_duplicate_files()

    # 降相似度
    print("3.降低文档相似度（加速版）...")
    file_processor = DocumentProcessor(config)
    file_processor.process_files()

    # 文件读取分类
    print("4.文档处理分类（加速版）...")
    classify = ClassifyFiles(config)
    # classify.handle_files_with_accelerate()
    classify.handle_files()

    # AI处理系统
    print("5.AI文档处理（加速版）...")
    # process = ProcessAPIAccelerate(config)
    process = ProcessAPIWithAccelerate(config)
    process.process_task()

    # 输出结果
    print("6.输出最终文档结果（加速版）...")
    refine = RefineResult(config)
    refine.process_result_files()
    print(f"结果保存在{config.clean_text_result_dir}")


def process_pipeline_no_accelerated(config):
    """
    非加速版的处理流程。
    """
    print("非加速模式已启用")

    # 文件遍历
    print("1.开始遍历文件...")
    traverser = DirectoryTraverser(config)
    traverser.traverse_directory()
    print(f"遍历完成，结果已保存到 {traverser.output_file}")

    # 去重
    print("2.开始文档去重...")
    file_checker = FileChecker(config)
    file_checker.find_duplicate_files()

    # 降相似度
    print("3.降低文档相似度...")
    file_processor = DocumentProcessor(config)
    file_processor.process_files()

    # 文件读取分类
    print("4.文档处理分类...")
    classify = ClassifyFiles(config)
    classify.handle_files()

    # AI处理系统
    print("5.AI文档处理...")
    process = ProcessAPIWithAccelerate(config)
    process.process_task()

    # 输出结果
    print("6.输出最终文档结果...")
    refine = RefineResult(config)
    refine.process_result_files()
    print(f"结果保存在{config.clean_text_result_dir}")


if __name__ == '__main__':
    total_config = combineArgs()
    if total_config.accelerate:
        process_pipeline_accelerated(total_config)
    else:
        process_pipeline_no_accelerated(total_config)













