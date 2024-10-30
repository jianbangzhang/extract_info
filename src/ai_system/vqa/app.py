# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : app.py
# Time       ：2024/10/7 11:35
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import base64
import json
import websocket
import os
import time
from natsort import natsorted
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.utils import save_result_to_txt,retry





class ImageToBase64Requester:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.received_messages=[]

    def read_image_and_encode(self, image_file_path):
        with open(image_file_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

    def write_output_txt(self, text ,vqa_dir):
        os.makedirs(vqa_dir,exist_ok=True)
        output_file=os.path.join(vqa_dir,"output.txt")
        with open(output_file, mode="w", encoding="utf-8") as f:
            f.write(text)
        print(f"Result has been saved to {output_file}!")

    def create_data_structure(self, encoded_image, ppt_prompt):
        data = {
            "header": {
                "traceId": "5cea1a38-c026-4fc8-8d79-5e1d44231d5a"
            },
            "parameter": {
                "chat": {
                    "adjustTokens": False,
                    "max_tokens": 4096,
                    "punish": 1.5,
                    "temperature": 0,
                    "top_k": 1
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "content": encoded_image,
                            "role": "user",
                            "content_type": "image"
                        },
                        {
                            "content": ppt_prompt,
                            "role": "user",
                            "content_type": "text"
                        }
                    ]
                }
            }
        }
        return data

    def on_open(self, ws, image_path, ppt_prompt):
        if os.path.isdir(image_path):
            for image_file in os.listdir(image_path):
                image_file_path = os.path.join(image_path, image_file)
                if os.path.isfile(image_file_path):
                    encoded_image = self.read_image_and_encode(image_file_path)
                    data_structure = self.create_data_structure(encoded_image, ppt_prompt)
                    ws.send(json.dumps(data_structure))
                    print(f"正在处理:{image_file_path}")
        else:
            encoded_image = self.read_image_and_encode(image_path)
            data_structure = self.create_data_structure(encoded_image, ppt_prompt)
            ws.send(json.dumps(data_structure))
            print(f"正在处理:{image_path}")

    def on_message(self, ws, message,vqa_dir):
        # print("Received message: " + message)
        message_data = json.loads(message)
        if 'payload' in message_data and 'choices' in message_data['payload']:
            for choice in message_data['payload']['choices']['text']:
                self.received_messages.append(choice['content'])

        if message_data['header']['status'] == 2:
            full_response = ''.join(self.received_messages)
            self.write_output_txt(full_response,vqa_dir)

    def on_error(self, ws, error):
        print("Error: " + str(error))

    def on_close(self, ws, close_status_code, message):
        print(f"WebSocket closed with status: {close_status_code}")


    def send_request(self, image_path, ppt_prompt,vqa_output_dir):
        self.ws = websocket.WebSocketApp(self.ws_url,
                                         on_open=lambda ws: self.on_open(ws, image_path,ppt_prompt),
                                         on_message=lambda ws, message: self.on_message(ws, message, vqa_output_dir),
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()



class VQAApi(object):
    def __init__(self, config):
        self.is_retry = config.is_retry
        self.max_retry_time = config.max_retry_time
        self.sleep_seconds = config.sleep_seconds
        self.ppt_prompt = config.ppt_prompt
        self.vqa_model_url = config.vqa_model_url
        self.max_thread = config.max_thread
        self.vqa_output_dir = config.vqa_output_dir
        self.vqa_request_parallel = config.vqa_request_parallel
        self.mode=config.mode

    def _run_vqa_with_retry(self, ppt_prompt,one_image_path, vqa_output_dir):
        """
        :param ppt_prompt:
        :param url:
        :param image_path_dir:
        :param output_dir:
        :return:
        """

        @retry(max_retry=self.max_retry_time, delay=self.sleep_seconds)
        def run_vqa(ppt_prompt,one_image_path, vqa_output_dir):
            """
            :param ppt_prompt:
            :param url:
            :param image_path_dir:
            :param output_dir:
            :return:
            """
            os.makedirs(vqa_output_dir,exist_ok=True)
            if not self.mode:
                image_requester = ImageToBase64Requester(self.vqa_model_url)
                image_requester.send_request(one_image_path, ppt_prompt,vqa_output_dir)
                vqa_result_path = os.path.join(vqa_output_dir, "output.txt")
            else:
                vqa_result_path = os.path.join(vqa_output_dir, "output.txt")
                with open(vqa_result_path, "w", encoding="utf-8") as f:
                    f.write("*多模态VQA" * 9)

            success_condition = os.path.exists(vqa_result_path) and os.path.isfile(vqa_result_path) and os.path.getsize(
                vqa_result_path) > 0
            code = 0 if success_condition else -1
            return code

        start_time = time.time()
        code = run_vqa(ppt_prompt, one_image_path, vqa_output_dir)
        print(f"VQA Request Time:{time.time() - start_time} seconds.")
        return code

    def _run_vqa(self, ppt_prompt, one_image_path, vqa_output_dir):
        """
        :param ppt_prompt:
        :param url:
        :param image_path_dir:
        :param output_dir:
        :return:
        """
        try:
            start_time = time.time()
            if not self.mode:
                image_requester = ImageToBase64Requester(self.vqa_model_url)
                image_requester.send_request(one_image_path, ppt_prompt, vqa_output_dir)
                vqa_result_path = os.path.join(vqa_output_dir, "output.txt")
            else:
                vqa_result_path = os.path.join(vqa_output_dir, "output.txt")
                with open(vqa_result_path, "w", encoding="utf-8") as f:
                    f.write("*多模态VQA"*9)

            print(f"VQA Request Time:{time.time() - start_time} seconds.")

            success_condition = os.path.exists(vqa_result_path) and os.path.isfile(vqa_result_path) and os.path.getsize(
                vqa_result_path) > 0
            code = 0 if success_condition else -1
        except Exception as e:
            print(str(e))
            code = -1
        return code

    def vqa_result(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as txt_file:
                content_string = txt_file.read()
        except:
            content_string = ""

        return content_string

    def _save_vqa_result(self, result_output_dir, process_result_dir, document_name):
        """
        :param output_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        total_page = []
        page_result_list = natsorted([page for page in os.listdir(result_output_dir) if not str(page).startswith(".")])
        txt_dir = os.path.join(process_result_dir, document_name, 'vqa')
        os.makedirs(txt_dir,exist_ok=True)
        for page_result in page_result_list:
            page_text = {}
            page_num = page_result
            txt_file_path = os.path.join(txt_dir, f"{page_num}.txt")
            vqa_result_path = os.path.join(result_output_dir,str(page_num), "output.txt")
            if not os.path.exists(vqa_result_path):
                continue
            content = self.vqa_result(file_path=vqa_result_path)
            save_result_to_txt(content, txt_file_path)
            page_text[page_num] = txt_file_path
            total_page.append(page_text)
        return total_page

    def _process_one_image(self, ppt_prompt, one_image_path, vqa_output_dir):
        if self.is_retry:
            code = self._run_vqa_with_retry(ppt_prompt, one_image_path, vqa_output_dir)
            if code == -1:
                self._run_vqa_with_retry(ppt_prompt, one_image_path, vqa_output_dir)
        else:
            code = self._run_vqa(ppt_prompt, one_image_path, vqa_output_dir)
            if code == -1:
                self._run_vqa(ppt_prompt, one_image_path, vqa_output_dir)


    def _process_images(self, image_path, ppt_prompt, output_dir, process_result_dir, document_name):
        """
        :param image_path:
        :param ppt_prompt:
        :param url:
        :param output_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        image_list = natsorted(os.listdir(image_path))
        for i, img in enumerate(image_list):
            image_file_path = os.path.join(image_path, img)
            vqa_result_dir = os.path.join(output_dir, document_name, str(i))
            os.makedirs(vqa_result_dir)
            self._process_one_image(ppt_prompt, image_file_path, vqa_result_dir)

        result_output_dir=os.path.join(output_dir, document_name)
        total_page = self._save_vqa_result(result_output_dir, process_result_dir, document_name)
        return total_page


    def _process_images_parallel(self,image_path, ppt_prompt, output_dir, process_result_dir, document_name):
        """
        :param image_path:
        :param ppt_prompt:
        :param url:
        :param output_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        image_list = natsorted(os.listdir(image_path))
        max_thread = min(min((cpu_count()+len(image_list))//2,self.max_thread),len(image_list))
        with ThreadPoolExecutor(max_workers = max_thread) as executor:
            future_to_image = {executor.submit(self._process_one_image, ppt_prompt,
                                               os.path.join(image_path, img), os.path.join(output_dir, document_name, str(i)),
                                               ): (i, img) for i,img in enumerate(image_list)}

            for future in as_completed(future_to_image):
                img = future_to_image[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f'Image {img} generated an exception: {exc}')

        result_output_dir = os.path.join(output_dir, document_name)
        total_page = self._save_vqa_result(result_output_dir, process_result_dir, document_name)
        return total_page


    def get_vqa_result(self, ppt_prompt, image_path, output_dir, process_result_dir, document_name):
        """
        :param ppt_prompt:
        :param image_path:
        :param output_dir:
        :param process_result_dir:
        :param document_name:
        :return:
        """
        try:
            if os.path.isdir(image_path):
                if self.vqa_request_parallel:
                    total_page = self._process_images_parallel(image_path, ppt_prompt, output_dir,
                                                                 process_result_dir, document_name)
                else:
                    total_page = self._process_images(image_path, ppt_prompt, output_dir,
                                                              process_result_dir, document_name)
                return total_page
        except Exception as e:
            print(str(e))
            return []


