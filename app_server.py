# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : app_server.py
# Time       ：2024/10/23 10:31
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
from datetime import datetime
from flask import Flask, request, send_file
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
from utils import unzip_decode

app = Flask(__name__)


def combineArgs(server_dict,dataset_dir):
    project_config = ProjectConfig()
    file_config = FileConfig(dataset_folder=dataset_dir)
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
        **server_dict
    }

    config(**total_config)
    return config


async def process_pipeline_accelerated(config):
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
    compress_folder(config.final_result_dir, config.zip_result_dir)
    zip_file = os.path.join(config.zip_result_dir, "result.zip")
    return zip_file


@app.route('/doc_ai', methods=['POST'])
async def process_file():
    print("收到请求...")
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    print(f"接收到文件: {file.filename}")
    tmp_dir = datetime.now().strftime('%Y%m%d%H%M%S')

    dataset_dir = os.path.join("datasets", tmp_dir)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(dataset_dir, exist_ok=True)
    zip_path = os.path.join("uploads", file.filename)
    file.save(zip_path)

    file_path = unzip_decode(zip_path, dataset_dir)
    server_dict = {"file_path": file_path}
    config = combineArgs(server_dict,dataset_dir)
    result_path = await process_pipeline_accelerated(config)
    print(result_path)
    return send_file(result_path, as_attachment=True, download_name='result.zip')



if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=9010)
