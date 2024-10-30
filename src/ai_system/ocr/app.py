# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : app.py
# Time       ：2024/10/7 11:50
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import ssl
import _thread as thread
import jsonpath
import websocket
import json
import os
import time
from natsort import natsorted
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
from .sample import ne_utils, aipass_client
from .data import *
from utils import save_result_to_txt,retry





class OCRApi(object):
    def __init__(self, config):
        self.is_retry = config.is_retry
        self.max_retry_time = config.max_retry_time
        self.sleep_seconds = config.sleep_seconds
        self.markdown_element_option = config.markdown_element_option
        self.sed_element_option = config.sed_element_option
        self.ocr_result_dir = config.ocr_result_dir
        self.max_thread = config.max_thread
        self.ocr_request_parallel=config.ocr_request_parallel

    def on_open(self, ws, request_data, ocr_res_dir):
        """
        :param ws:
        :param request_data:
        :param ocr_res_dir:
        :return:
        """
        def run(request_data, ocr_res_dir):
            try:
                os.makedirs(ocr_res_dir,exist_ok=True)
                ne_utils.del_file(ocr_res_dir)
                exist_audio = jsonpath.jsonpath(request_data, "$.payload.*.audio")
                exist_video = jsonpath.jsonpath(request_data, "$.payload.*.video")
                multi_mode = True if exist_audio and exist_video else False

                frame_rate = None
                if jsonpath.jsonpath(request_data, "$.payload.*.frame_rate"):
                    frame_rate = jsonpath.jsonpath(request_data, "$.payload.*.frame_rate")[0]
                time_interval = 40
                if frame_rate:
                    time_interval = round((1 / frame_rate) * 1000)

                media_path2data = aipass_client.prepare_req_data(request_data)
                aipass_client.send_ws_stream(ws, request_data, media_path2data, multi_mode, time_interval)
            except Exception as e:
                print(f"Error during run: {e}")
                self.code = -1  # 发送数据时出错，标记失败

        thread.start_new_thread(run, (request_data, ocr_res_dir,))

    def on_message(self, ws, message, output_dir):
        """
        :param ws:
        :param message: 收到的 WebSocket 消息
        """
        # print(f"Message received: {message}")
        # 在这里判断消息是否表示成功
        if "success" in message or "some_success_indicator" in message:  # 根据返回的格式调整
            self.code = 0  # 请求成功
        else:
            self.code = -1  # 请求失败

        aipass_client.deal_message(ws, message,output_dir)

    def on_error(self, ws, error):
        """
        :param ws:
        :param error: WebSocket 错误
        """
        print(f"### error: {error}")
        self.code = -1

    def on_close(self, ws, *arg):
        """
        :param ws:
        :param *arg: WebSocket 关闭时的参数
        """
        print("")

    def _run_ocr(self, request_url, zip_file_path, ocr_res_dir):
        """
        :param request_url:
        :param zip_file_path:
        :param ocr_res_dir:
        :return: 返回请求状态的code，0为成功，-1为失败
        """
        try:
            start_time = time.time()
            request_data = get_request_data(zip_file_path, self.markdown_element_option, self.sed_element_option)

            request_data['header']['app_id'] = APPId
            auth_request_url = ne_utils.build_auth_request_url(request_url, "GET", APIKey, APISecret)
            websocket.enableTrace(False)
            ws = websocket.WebSocketApp(auth_request_url,
                                        on_message=lambda ws, message: self.on_message(ws, message, ocr_res_dir),
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            ws.on_open = lambda ws: self.on_open(ws, request_data, ocr_res_dir)
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

            print(f"OCR Request Time:{time.time() - start_time} seconds.")

            result_file_path = os.path.join(ocr_res_dir, "result.utf8")
            success_condition = os.path.exists(result_file_path) and os.path.isfile(result_file_path) and os.path.getsize(result_file_path) > 0
            code = 0 if success_condition else -1
        except Exception as e:
            print(str(e))
            code = -1
        return code


    def _run_ocr_with_retry(self, request_url, zip_file_path, ocr_res_dir):
        """
        :param request_url:
        :param zip_file_path:
        :param ocr_res_dir:
        :return:
        """
        @retry(max_retry=self.max_retry_time,delay=self.sleep_seconds)
        def run_ocr(request_url,zip_file_path,ocr_res_dir):
            """
            :param request_url:
            :param zip_file_path:
            :param ocr_res_dir:
            :return:
            """
            request_data = get_request_data(zip_file_path,self.markdown_element_option,self.sed_element_option)

            request_data['header']['app_id'] = APPId
            auth_request_url = ne_utils.build_auth_request_url(request_url, "GET", APIKey, APISecret)
            websocket.enableTrace(False)
            ws = websocket.WebSocketApp(auth_request_url,
                                        on_message=lambda ws, message: self.on_message(ws, message, ocr_res_dir),
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            ws.on_open = lambda ws: self.on_open(ws, request_data, ocr_res_dir)
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

            result_file_path=os.path.join(ocr_res_dir,"result.utf8")
            success_condition = os.path.exists(result_file_path) and os.path.isfile(result_file_path) and os.path.getsize(result_file_path) > 0
            code = 0 if success_condition else -1
            return code

        start_time = time.time()
        code = run_ocr(request_url,zip_file_path,ocr_res_dir)
        print(f"OCR Request Time:{time.time()-start_time} seconds.")
        return code


    def ocr_result(self,file_path):
        """
        :param file_path:
        :return:
        """
        content_dict_lst=[]
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                content = content.replace('"}{"','"},{"')
                content = content.strip()

                if len(content)>0:
                    content = '[' +content + ']'
                else:
                    content = '[]'
                try:
                    content_dict_lst = eval(content)
                except:
                    try:
                        content_dict_lst = json.loads(content)
                    except Exception as e:
                        print(f"Error: {e}")
                        return []
        return content_dict_lst

    def _save_ocr_result(self,output_dir,process_result_dir, document_name):
        """
        :param output_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        page_text = {}
        page_result_list = natsorted([path for path in os.listdir(output_dir) if len(os.listdir(os.path.join(output_dir, path)))])
        txt_dir = os.path.join(process_result_dir, document_name)
        for page in page_result_list:
            page_num=page
            txt_file_path = os.path.join(txt_dir, f"{page_num}.txt")
            ocr_result_path = os.path.join(output_dir,page ,"result.utf8")
            content = self.ocr_result(file_path=ocr_result_path)
            save_result_to_txt(content, txt_file_path)
            page_text[page_num] = txt_file_path
        return page_text


    def process_one_file(self,request_url, zip_path, ocr_res_dir,process_result_dir,document_name,ocr_before=False,content_dict_lst=None):
        """
        :param request_url:
        :param zip_path:
        :param ocr_res_dir:
        :param process_result_dir:
        :param document_name:
        :param ocr_before:
        :param content_dict_lst:
        :return:
        """
        page_text = {}
        file_name_with_extention = os.path.basename(zip_path)
        file_name, _ = os.path.splitext(file_name_with_extention)
        print(f"OCR正在处理{zip_path}")
        txt_file_path=os.path.join(process_result_dir,document_name,f"{file_name}.txt")
        ocr_save_dir=os.path.join(ocr_res_dir,file_name)
        os.makedirs(ocr_res_dir,exist_ok=True)

        if not ocr_before:
            if self.is_retry:
                code = self._run_ocr_with_retry(request_url, zip_path, ocr_save_dir)
                if code == -1:
                    self._run_ocr_with_retry(request_url, zip_path, ocr_save_dir)
            else:
                code=self._run_ocr(request_url, zip_path, ocr_save_dir)
                if code == -1:
                    self._run_ocr(request_url, zip_path, ocr_save_dir)

            result_file_path =os.path.join(ocr_save_dir,"result.utf8")
            content_dict_lst = self.ocr_result(result_file_path)
        else:
            content_dict_lst = content_dict_lst

        content_dict_string=json.dumps(content_dict_lst,ensure_ascii=False)
        save_result_to_txt(content_dict_string,txt_file_path)
        page_text[file_name] = txt_file_path
        return page_text,content_dict_lst

    def _process_files_in_parallel_ocr(self,zip_file_path, request_url, ocr_res_dir, process_result_dir, document_name, ocr_before, ocr_result, text_page):
        """
        :param zip_file_path:
        :param request_url:
        :param ocr_res_dir:
        :param process_result_dir:
        :param document_name:
        :param ocr_before:
        :param ocr_result:
        :param text_page:
        :return:
        """
        zip_list = natsorted(os.listdir(zip_file_path))
        ocr_output_dir = os.path.join(ocr_res_dir, document_name)

        max_thread = min(min((cpu_count() + len(zip_list)) // 2, self.max_thread),len(zip_list))
        with ThreadPoolExecutor(max_workers=max_thread) as executor:
            future_to_zip = {
                executor.submit(self.process_one_file, request_url, os.path.join(zip_file_path, zip_file),
                                ocr_output_dir, process_result_dir, document_name, ocr_before, ocr_result): zip_file
                for zip_file in zip_list}

            for future in as_completed(future_to_zip):
                zip_file = future_to_zip[future]
                try:
                    page_text, _ = future.result()
                    text_page.append(page_text)
                except Exception as exc:
                    print(f'{zip_file} generated an exception: {exc}')

        page_text = self._save_ocr_result(ocr_output_dir, process_result_dir, document_name)
        return page_text


    def _process_files_no_parallel_ocr(self,zip_file_path, request_url, ocr_res_dir, process_result_dir, document_name, ocr_before, ocr_result, text_page):
        """
        :param zip_file_path:
        :param request_url:
        :param ocr_res_dir:
        :param process_result_dir:
        :param document_name:
        :param ocr_before:
        :param ocr_result:
        :param text_page:
        :return:
        """
        zip_list = natsorted(os.listdir(zip_file_path))
        ocr_output_dir = os.path.join(ocr_res_dir, document_name)

        for zip_file in zip_list:
            try:
                zip_path = os.path.join(zip_file_path, zip_file)
                page_text, _ = self.process_one_file(request_url, zip_path,ocr_output_dir, process_result_dir, document_name, ocr_before, ocr_result)
                text_page.append(page_text)
            except Exception as e:
                print(str(e))
                continue

        page_text = self._save_ocr_result(ocr_output_dir, process_result_dir, document_name)
        return page_text


    def get_ocr_result(self,request_url,zip_file_path,ocr_res_dir,process_result_dir,document_name,ocr_before=False,ocr_result=None):
        """
        :param request_url:
        :param zip_file_path:
        :param ocr_res_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        text_page=[]
        try:
            if os.path.isdir(zip_file_path):
                if self.ocr_request_parallel:
                    self._process_files_in_parallel_ocr(zip_file_path, request_url, ocr_res_dir, process_result_dir, document_name, ocr_before, ocr_result, text_page)
                else:
                    self._process_files_no_parallel_ocr(zip_file_path, request_url, ocr_res_dir, process_result_dir, document_name, ocr_before, ocr_result, text_page)
                return text_page
        except Exception as e:
            print(str(e))
            return []



    def get_ocr_one_page_result(self,request_url,zip_file_path,ocr_res_dir,process_result_dir,document_name):
        """
        :param request_url:
        :param zip_file_path:
        :param ocr_res_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        try:
            if os.path.isdir(zip_file_path):
                zip_file=natsorted(os.listdir(zip_file_path))[0]
                zip_path=os.path.join(zip_file_path,zip_file)
                _,text_dict=self.process_one_file(request_url, zip_path, ocr_res_dir, process_result_dir,document_name)
                return text_dict
        except Exception as e:
            print(str(e))
            return {}









