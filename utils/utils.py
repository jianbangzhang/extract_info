# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : utils.py
# Time       ：2024/10/8 10:18
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import shutil
import os
import json
import time
import zipfile
from natsort import natsorted
import chardet



def read_files(path_file):
    """
    :param path_file:
    :return:
    """
    with open(path_file, "r", encoding="utf-8") as f:
        contents = f.readlines()
        path_list = [line.split("\t\t")[-1].strip() for line in contents]
        path_list = natsorted(path_list)
    return path_list

def read_json_file(input_data_path):
    """
    :param input_data_path:
    :return:
    """
    try:
        with open(input_data_path, 'r',encoding="utf-8") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        print(f"File {input_data_path} is not a valid JSON.")
        return {}

def get_file_type(file_path):
    """
    :param file_path:
    :return:
    """
    file_name = os.path.basename(file_path)
    _, file_type = os.path.splitext(file_name)
    return file_type.lower()


def get_path_info(file_path):
    """
    :param file_path:
    :return:
    """
    file_name_with_extension = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(file_name_with_extension)

    folder_path = os.path.dirname(file_path)
    return folder_path,file_name,file_extension



def copy_file(src, dst):
    """
    :param src:
    :param dst:
    :return:
    """

    try:
        os.makedirs(os.path.dirname(dst),exist_ok=True)
        shutil.copy(src, dst)
        print(f"文件已成功从 '{src}' 复制到 '{dst}'")
    except:
        print("复制文件时发生了一个未知错误。")



def save_result_to_txt(data, txt_file_path):
    """
    :param data: 要保存的数据
    :param data_dict: 包含其他要保存信息的字典
    :param file_name: 保存的文件名，不包括扩展名
    """
    os.makedirs(os.path.dirname(txt_file_path), exist_ok=True)
    if len(data)==0:
        data=""

    with open(txt_file_path, 'w', encoding='utf-8') as file:
        file.write(f"{data}\n")


def save_result_to_json(data_dict, json_path):
    """
    :param data_dict: 要保存的字典数据
    :param json_path: 保存JSON文件的路径
    """
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, ensure_ascii=False, indent=4)


def read_txt_file(file_path):
    """
    :param file_path:
    :return:
    """
    with open(file_path,"r",encoding="utf-8") as f:
        return f.read()



def retry(max_retry, delay):
    """
    :param max_retry:
    :param delay:
    :return:
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_count = 0
            code=-1
            while retry_count < max_retry and code!=0:
                code = func(*args, **kwargs)
                if code==-1:
                    time.sleep(delay)
                retry_count+=1
            return code
        return wrapper
    return decorator


def find_result_name(data_dict):
    """
    :param data_dict:
    :return:
    """
    key_lst=[]
    print(data_dict)
    for key in data_dict:
        if "result" in str(key):
            key_lst.append(key)
        else:
            continue
    return key_lst


def unzip(zip_path, extract_path):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
        print(f"文件已成功解压到 {extract_path}")


def unzip_decode_old(zip_path, extract_path):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            try:
                file_info.filename = file_info.filename.encode('cp437').decode('utf-8')
            except UnicodeDecodeError:
                file_info.filename = file_info.filename.encode('cp437').decode('latin1')

            zip_ref.extract(file_info, extract_path)
        print(f"文件已成功解压到 {extract_path}")

    lst = [file for file in os.listdir(extract_path) if not (file.startswith(".") or file.startswith("_"))]

    for f in lst:
        if f.startswith("_") or f.startswith("."):
            continue
        path = os.path.join(extract_path, f)
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return extract_path


def unzip_decode(zip_path, extract_path):
    """
    解压指定路径下的 ZIP 文件，自动检测文件名编码并尝试多种备选编码，避免乱码。

    :param zip_path: ZIP 文件的路径
    :param extract_path: 要解压到的目标文件夹路径
    :return: 解压后的文件夹路径，或解压的主要文件路径
    """
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    encodings = ['utf-8', 'latin1', 'gbk', 'shift_jis']

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            detected_encoding = chardet.detect(file_info.filename.encode('cp437'))['encoding']
            if detected_encoding:
                try:
                    file_info.filename = file_info.filename.encode('cp437').decode(detected_encoding)
                except UnicodeDecodeError:
                    print(f"无法使用检测到的编码 {detected_encoding} 解码文件名：{file_info.filename}")

            if not detected_encoding or 'UnicodeDecodeError' in locals():
                for enc in encodings:
                    try:
                        file_info.filename = file_info.filename.encode('cp437').decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"文件名解码失败，跳过文件：{file_info.filename}")
                    continue

            zip_ref.extract(file_info, extract_path)
        print(f"文件已成功解压到 {extract_path}")

    lst = [file for file in os.listdir(extract_path) if not (file.startswith(".") or file.startswith("_"))]

    for f in lst:
        if f.startswith("__") or f.startswith("."):
            continue
        path = os.path.join(extract_path, f)
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            doc_name = os.path.splitext(f)[0]
            new_dir = os.path.join(extract_path,doc_name)
            new_file_path = os.path.join(new_dir,f)
            copy_file(path,new_file_path)
            os.remove(path)
            return new_dir
        else:
            raise ValueError





def unzip_decode1(zip_path, extract_path):
    """
    解压指定路径下的 ZIP 文件，自动检测文件名编码并尝试多种备选编码，避免乱码。

    :param zip_path: ZIP 文件的路径
    :param extract_path: 要解压到的目标文件夹路径
    :return: 解压后的文件夹路径，或解压的主要文件路径
    """
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    encodings = ['utf-8', 'latin1', 'gbk', 'shift_jis']

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            detected_encoding = chardet.detect(file_info.filename.encode('cp437'))['encoding']
            if detected_encoding:
                try:
                    file_info.filename = file_info.filename.encode('cp437').decode(detected_encoding)
                except UnicodeDecodeError:
                    print(f"无法使用检测到的编码 {detected_encoding} 解码文件名：{file_info.filename}")

            if not detected_encoding or 'UnicodeDecodeError' in locals():
                for enc in encodings:
                    try:
                        file_info.filename = file_info.filename.encode('cp437').decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"文件名解码失败，跳过文件：{file_info.filename}")
                    continue

            zip_ref.extract(file_info, extract_path)
        print(f"文件已成功解压到 {extract_path}")

    # 获取解压文件夹中非隐藏文件的列表
    lst = [file for file in os.listdir(extract_path) if not (file.startswith(".") or file.startswith("_"))]

    # 返回解压路径中的主要文件或文件夹
    for f in lst:
        if f.startswith("_") or f.startswith("."):
            continue
        path = os.path.join(extract_path, f)
        if os.path.isdir(path):
            return path  # 如果是文件夹，返回文件夹路径
        elif os.path.isfile(path):
            return extract_path  # 如果是文件，返回解压路径


def compress_folder(folder_path, output_folder):
    """
    压缩指定文件夹为 result.zip 文件并放在指定输出文件夹中

    :param folder_path: 要压缩的文件夹路径
    :param output_folder: 存放压缩文件的文件夹路径
    """
    os.makedirs(output_folder,exist_ok=True)

    output_zip_path = os.path.join(output_folder, "result")
    shutil.make_archive(output_zip_path, 'zip', folder_path)
    print(f"文件夹 '{folder_path}' 已成功压缩为 '{output_zip_path}.zip'")


def convert2md(total_pages):
    total_md=[]
    for data_dic in total_pages:
        md_dict={}
        md_lst=[]
        page_id,path=list(*data_dic.items())
        md_dir = os.path.join(os.path.dirname(path),"ocr")
        os.makedirs(md_dir,exist_ok=True)
        if os.path.exists(path):
            content_lst = read_txt_file(path)
            try:
                content_lst = eval(content_lst)
            except:
                content_lst = content_lst

            for data_dict in content_lst:
                doc_lst = data_dict["document"]
                for dic in doc_lst:
                    content = dic["value"]
                    md_lst.append(content)
            md_content = "\n".join(md_lst)
            output_md_path = os.path.join(md_dir,f"{page_id}.md")

            with open(output_md_path, 'w', encoding='utf-8') as file:
                file.write(md_content)
            md_dict[page_id]=output_md_path
            total_md.append(md_dict)
        else:
            continue
    return total_pages


