# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : classify.py
# Time       ：2024/10/8 10:07
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import warnings
import os
import json
from utils import read_files,get_file_type,copy_file
from .check_images import DocumentInspector
from .file_io import FileIOApi,FolderZipper,ExcelReader
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings("ignore")




class ClassifyFiles(object):
    def __init__(self, config):
        """
        :param config:
        """
        unique_path_file=config.unique_file_path
        self.files_list = read_files(unique_path_file)
        self.inspector = DocumentInspector()
        self.fileIO = FileIOApi()
        self.folder_zipper = FolderZipper()
        self.excel_reader = ExcelReader()
        self.pptx_pdf_dir=config.pptx_pdf_dir
        self.docx_pdf_dir=config.docx_pdf_dir
        self.schema = config.schema
        self.input_data_path=config.input_data_path
        self.zip_image_size=config.zip_image_size
        self.text_content_dir=config.text_content_dir
        self.mix_data_dir=config.mix_data_dir
        self.process_image_schema=config.process_image_schema
        self.max_thread=config.max_thread
        self.tmp_data_dir = config.tmp_data_dir

        self.word_img_dir = config.word_img_dir
        self.single_img_dir = config.single_img_dir
        self.doc_zip_dir = config.doc_zip_dir
        self.single_zip_dir = config.single_zip_dir
        self.excel_dir = config.excel_dir
        self.audio_dir = config.audio_dir
        self.video_dir = config.video_dir

        self.timeout = config.task_timeout
        self.set_runtime = config.set_runtime
        self.init()

    def init(self):
        os.makedirs(self.word_img_dir, exist_ok=True)
        os.makedirs(self.single_img_dir, exist_ok=True)
        os.makedirs(self.excel_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)

        with open(self.input_data_path, 'w', encoding='utf-8') as file:
            json.dump([], file)

    def _process_pdf(self,file_path):
        """
        :param file_path:
        :return:
        """
        def transform_image(file_path):
            """
            :param file_path:
            :return:
            """
            img_dir = os.path.join(self.word_img_dir, file_name)
            self.fileIO.pdf_all_to_image(file_path, img_dir)

            output_zip_dir = os.path.join(self.doc_zip_dir, file_name)
            self._zip_files(img_dir, output_zip_dir)

            pdf_path_data["images"] = img_dir
            pdf_path_data["zip"] = output_zip_dir
            return pdf_path_data

        def read_pdf_text(file_path):
            """
            :param file_path:
            :return:
            """
            content = self.fileIO.read_pdf(file_path)
            txt_path = os.path.join(self.text_content_dir, file_name + ".txt")
            self.fileIO.write_text(content, txt_path)
            pdf_path_data["text"] = txt_path
            return pdf_path_data

        def read_text_image(file_path):
            """
            :param file_path:
            :return:
            """
            image_dir = os.path.join(self.mix_data_dir, file_name, "image")
            os.makedirs(image_dir, exist_ok=True)

            self.fileIO.pdf_page_to_image(file_path, image_dir, res_lst)
            output_dir = os.path.join(self.mix_data_dir, file_name, "text")
            os.makedirs(output_dir, exist_ok=True)
            self.fileIO.read_pdf_pages(file_path, res_lst, output_dir)

            output_zip_dir = os.path.join(self.mix_data_dir, file_name, "zip")
            os.makedirs(output_zip_dir, exist_ok=True)
            self._zip_files(image_dir, output_zip_dir, zip_image_size=1, remain_raw_name=True)

            pdf_path_data["images"] = image_dir
            pdf_path_data["zip"] = output_zip_dir
            pdf_path_data["text"] = output_dir
            pdf_path_data["image_page"] = res_lst
            return pdf_path_data

        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        pdf_path_data={"type":"pdf","file":file_name,"path":file_path,"images":"","zip":"","text":"","image_page":[]}

        if self.schema == "all":
            pdf_path_data=transform_image(file_path)
        elif self.schema == "part":
            res_lst,total_page = self.inspector.check_images_tables_in_pdf(file_path)
            if res_lst:
                if len(res_lst)==total_page or self.process_image_schema=="pure":
                    pdf_path_data = transform_image(file_path)
                else:
                    pdf_path_data=read_text_image(file_path)
            else:
                pdf_path_data=read_pdf_text(file_path)
        elif self.schema == "zero":
            pdf_path_data=read_pdf_text(file_path)
        else:
            raise NotImplementedError
        return pdf_path_data


    def _process_docx(self,file_path):
        """
        :param file_path:
        :return:
        """
        def transform_image(file_path,transform_pdf_before=False,pdf_file_path=None):
            img_dir = os.path.join(self.word_img_dir, file_name)
            self.fileIO.docx_all_to_image(file_path, self.docx_pdf_dir, self.word_img_dir,
                                          transform_pdf_before=transform_pdf_before,pdf_file_path=pdf_file_path)

            output_zip_dir = os.path.join(self.doc_zip_dir, file_name)
            self._zip_files(img_dir, output_zip_dir)

            pdf_path = os.path.join(self.docx_pdf_dir, file_name + ".pdf")
            docx_path_data["file"] = file_name
            docx_path_data["images"] = img_dir
            docx_path_data["zip"] = output_zip_dir
            docx_path_data["transform"] = pdf_path
            return docx_path_data

        def read_docx_text(file_path):
            """
            :param file_path:
            :return:
            """
            content = self.fileIO.read_docx(file_path)
            txt_path = os.path.join(self.text_content_dir, file_name + ".txt")
            self.fileIO.write_text(content, txt_path)
            docx_path_data["text"] = txt_path
            return docx_path_data

        def read_text_image(file_path):
            """
            :param file_path:
            :return:
            """
            image_dir = os.path.join(self.mix_data_dir, file_name, "image")
            os.makedirs(image_dir, exist_ok=True)

            self.fileIO.pdf_page_to_image(file_path, image_dir, res_lst)
            output_dir = os.path.join(self.mix_data_dir, file_name, "text")
            os.makedirs(output_dir, exist_ok=True)
            self.fileIO.read_pdf_pages(file_path, res_lst, output_dir)

            output_zip_dir = os.path.join(self.mix_data_dir, file_name, "zip")
            os.makedirs(output_zip_dir, exist_ok=True)
            self._zip_files(image_dir, output_zip_dir, zip_image_size=1, remain_raw_name=True)

            docx_path_data["images"] = image_dir
            docx_path_data["zip"] = output_zip_dir
            docx_path_data["text"] = output_dir
            docx_path_data["image_page"] = res_lst
            docx_path_data["transform"]=file_path
            return docx_path_data

        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        docx_path_data = {"type": "docx", "file": file_name, "path": file_path, "images": "","zip":"", "text": "","transform":"","image_page":[]}
        if self.schema == "all":
            docx_path_data=transform_image(file_path)

        elif self.schema == "part":
            res_lst_from_docx,_=self.inspector.check_images_tables_in_docx(file_path)
            if len(res_lst_from_docx)>0:
                pdf_file_name = os.path.basename(file_path).replace("docx", "pdf")
                pdf_file_path = os.path.join(self.docx_pdf_dir, pdf_file_name)
                self.fileIO.docx_to_pdf(file_path, pdf_file_path)
                res_lst, total_page = self.inspector.check_images_tables_in_pdf(pdf_file_path)

                if len(res_lst) == total_page or self.process_image_schema == "pure":
                    docx_path_data = transform_image(file_path,transform_pdf_before=True,pdf_file_path=pdf_file_path)
                else:
                    docx_path_data = read_text_image(pdf_file_path)
            else:
                docx_path_data = read_docx_text(file_path)

        elif self.schema=="zero":
            docx_path_data = read_docx_text(file_path)
        else:
            raise NotImplementedError

        return docx_path_data

    def _process_pptx(self,file_path):
        """
        :param file_path:
        :return:
        """
        def transform_image(file_path):
            """
            :param file_path:
            :return:
            """
            img_dir = os.path.join(self.word_img_dir, file_name)
            os.makedirs(img_dir,exist_ok=True)
            self.fileIO.pptx_all_to_image(file_path, self.pptx_pdf_dir, self.word_img_dir)

            output_zip_dir = os.path.join(self.doc_zip_dir, file_name)
            self._zip_files(img_dir, output_zip_dir)

            pdf_path = os.path.join(self.pptx_pdf_dir, file_name + ".pdf")
            pptx_path_data["file"] = file_name
            pptx_path_data['images'] = img_dir
            pptx_path_data["zip"] = output_zip_dir
            pptx_path_data["transform"] = pdf_path
            return pptx_path_data

        def read_pptx_text(file_path):
            """
            :param file_path:
            :return:
            """
            content = self.fileIO.read_pptx(file_path)
            txt_path = os.path.join(self.text_content_dir, file_name + ".txt")
            self.fileIO.write_text(content, txt_path)
            pptx_path_data["text"] = txt_path
            return pptx_path_data

        def read_text_image(file_path):
            """
            :param file_path:
            :return:
            """
            image_dir = os.path.join(self.mix_data_dir, file_name, "image")
            os.makedirs(image_dir, exist_ok=True)

            pptx_file_name = os.path.basename(file_path)
            pdf_file_name = pptx_file_name.replace("pptx", "pdf")
            pdf_file_path = os.path.join(self.pptx_pdf_dir, pdf_file_name)
            self.fileIO.pptx_page_to_image(file_path, pdf_file_path, image_dir,res_lst)
            output_dir = os.path.join(self.mix_data_dir, file_name, "text")
            os.makedirs(output_dir, exist_ok=True)
            self.fileIO.read_pptx_pages(file_path, res_lst, output_dir)

            output_zip_dir = os.path.join(self.mix_data_dir, file_name, "zip")
            os.makedirs(output_zip_dir, exist_ok=True)
            self._zip_files(image_dir, output_zip_dir, zip_image_size=1, remain_raw_name=True)

            pptx_path_data["images"] = image_dir
            pptx_path_data["zip"] = output_zip_dir
            pptx_path_data["text"] = output_dir
            pptx_path_data["image_page"] = res_lst
            pptx_path_data["transform"] = pdf_file_path
            return pptx_path_data

        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        pptx_path_data = {"type": "pptx", "file": file_name, "path": file_path, "images": "","zip":"", "text": "","transform":"","image_page":[]}

        if self.schema == "all":
            pptx_path_data=transform_image(file_path)
        elif self.schema == "part":
            res_lst,total_pages = self.inspector.check_images_tables_in_pptx(file_path)
            if res_lst:
                if len(res_lst)==total_pages or self.process_image_schema=="pure":
                    pptx_path_data = transform_image(file_path)
                else:
                    pptx_path_data=read_text_image(file_path)
            else:
                pptx_path_data=read_pptx_text(file_path)
        elif self.schema=="zero":
            pptx_path_data=read_pptx_text(file_path)
        else:
            raise NotImplementedError
        return pptx_path_data

    def _process_excel(self,file_path):
        """
        :param file_path:
        :return:
        """
        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        excel_path_data = {"type": "excel", "file": file_name, "path": file_path}
        markdown_dir= os.path.join(self.excel_dir,file_name)
        os.makedirs(markdown_dir,exist_ok=True)
        total_result=self.excel_reader.process_excel(file_path,markdown_dir)
        excel_path_data["result"]=total_result
        return excel_path_data

    def _process_video(self,file_path):
        """
        :param file_path:
        :return:
        """
        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        out_video_path = os.path.join(self.tmp_data_dir, file_name, file_name_with_extension)
        copy_file(file_path, out_video_path)
        video_path_data = {"type": "video", "file": file_name, "zip": "", "path": file_path}
        output_zip = os.path.join(self.video_dir,file_name, file_name + ".zip")
        self._zip_files(file_path, output_zip)
        video_path_data["zip"] = os.path.dirname(output_zip)
        return video_path_data

    def _process_audio(self,file_path):
        """
        :param file_path:
        :return:
        """
        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        out_audio_path = os.path.join(self.tmp_data_dir, file_name, file_name_with_extension)
        copy_file(file_path, out_audio_path)
        audio_path_data = {"type": "audio", "file": file_name, "zip": "", "path": file_path}
        output_zip = os.path.join(self.audio_dir, file_name, file_name + ".zip")
        self._zip_files(file_path, output_zip)
        audio_path_data["zip"] = os.path.dirname(output_zip)
        return audio_path_data

    def _process_image(self,file_path):
        """
        :param file_path:
        :return:
        """
        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        out_image_path=os.path.join(self.tmp_data_dir,file_name,file_name_with_extension)
        copy_file(file_path,out_image_path)
        image_path_data = {"type": "image", "file": file_name, "zip": "", "path": out_image_path, "images":os.path.dirname(out_image_path)}
        output_zip = os.path.join(self.single_zip_dir, file_name, file_name + ".zip")
        self._zip_files(file_path, output_zip)
        image_path_data["zip"] = os.path.dirname(output_zip)
        return image_path_data

    def _process_txt(self,file_path):
        """
        :param file_path:
        :return:
        """
        file_name_with_extension = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name_with_extension)
        image_path_data = {"type": "txt", "file": file_name, "zip": "", "path": file_path}
        return image_path_data


    def _zip_files(self,input_path,output_zip_file,zip_image_size=None,remain_raw_name=False):
        """
        :param input_path:
        :param output_zip_file:
        :param zip_image_size:
        :param remain_raw_name:
        :return:
        """
        os.makedirs(os.path.dirname(output_zip_file),exist_ok=True)
        if zip_image_size is None:
            zip_image_size=self.zip_image_size

        if not output_zip_file.endswith(".zip"):
            self.folder_zipper.zip_folder_many(input_path,zip_image_size,output_zip_file,remain_raw_name)
        else:
            self.folder_zipper.zip_folder(input_path,output_zip_file)

    def process_one_file(self, file_path):
        """
        :param file_path:
        :return:
        """
        file_type = get_file_type(file_path)

        if file_type == ".pdf":
            data_path=self._process_pdf(file_path)

        elif file_type == ".docx":
            data_path=self._process_docx(file_path)

        elif file_type == ".pptx":
            data_path=self._process_pptx(file_path)

        elif file_type in [".xlsx",".xls"]:
            data_path=self._process_excel(file_path)

        elif file_type in [".wav", ".mp4"]:
            data_path=self._process_video(file_path)

        elif file_type in [".mp3"]:
            data_path=self._process_audio(file_path)

        elif file_type in [".png", ".jpg", ".jpeg"]:
            data_path=self._process_image(file_path)

        elif file_type in [".txt"]:
            data_path=self._process_txt(file_path)

        else:
            print(f"{file_path} is not implemented!")
            raise NotImplementedError

        return data_path

    def _append_data_to_json(self, new_data):
        """
        :param new_data: 要追加的新数据，类型应为字典
        """
        try:
            with open(self.input_data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            data.append(new_data)

            with open(self.input_data_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                print("路径写入成功。")

        except Exception as e:
            print(f"json写入出现错误：{str(e)}")
            raise e

    def handle_files(self):
        for i, file_path in enumerate(self.files_list):
            print(f"正在读取文件：{file_path}")

            try:
                data_info_dict=self.process_one_file(file_path)
                self._append_data_to_json(data_info_dict)
                print(f"{file_path}处理成功！")
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
                continue

    def handle_files_with_accelerate(self):
        """
        Handle files in parallel using ThreadPoolExecutor to accelerate file processing.
        """
        max_workers = min(min((cpu_count()+len(self.files_list))//2,self.max_thread),len(self.files_list))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.process_one_file, file_path): file_path for file_path in self.files_list}

            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    if self.set_runtime:
                        data_info_dict = future.result(timeout=self.timeout)
                    else:
                        data_info_dict = future.result()
                    self._append_data_to_json(data_info_dict)
                    print(f"{file_path} 处理成功！")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")






            









