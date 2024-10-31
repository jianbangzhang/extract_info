# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : app_client.py
# Time       ：2024/10/23 10:39
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
import requests



def ai_doc_query(file_path, output_path='result.zip'):
    url = 'http://127.0.0.1:9010/doc_ai'
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post(url, files=files, timeout=3000)

    if response.status_code == 200:
        with open(output_path, 'wb') as output_file:
            output_file.write(response.content)
        print(f"Server请求成功，结果已保存为 {output_path}")
    else:
        print(f"文件上传失败: {response.text}")




if __name__ == '__main__':
    zip_file_path = 'datasets/pptx.zip'
    output_path = 'result.zip'
    ai_doc_query(zip_file_path, output_path)
