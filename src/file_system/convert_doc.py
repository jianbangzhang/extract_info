# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : convert_doc.py
# Time       ：2024/10/8 15:50
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""
import os
import shutil
import subprocess
from moviepy.editor import VideoFileClip
import platform
from exceptions import ConvertTOPdfError,ExtractAudioError


class DocumentConverter:
    def doc_to_pdf(self, doc_file_path, pdf_file_path, move_to_directory):
        """
        :param doc_file_path:
        :param pdf_file_path:
        :param move_to_directory:
        :return:
        """
        current_os = platform.system()

        if current_os == 'Darwin':
            libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        elif current_os == 'Linux':
            libreoffice_path = 'libreoffice'
        else:
            raise OSError("当前系统不支持。请确保系统为 macOS 或 Linux。")

        try:
            subprocess.run([libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_file_path),
                 doc_file_path], check=True)
            print(f"成功将 {doc_file_path} 转换为 PDF 格式: {pdf_file_path}")
        except ConvertTOPdfError as e:
            print(f"出现错误: {e}")

        os.makedirs(move_to_directory,exist_ok=True)
        doc_file_name = os.path.basename(doc_file_path)
        move_to_path = os.path.join(move_to_directory, doc_file_name)
        shutil.move(doc_file_path, move_to_path)
        print(f"成功把{doc_file_path}转为pdf,并移到路径:{move_to_directory}")


    def extract_audio_from_video(self,video_path, output_audio_path,move_to_directory):
        """
        :param video_path:
        :param output_audio_path:
        :param move_to_directory:
        :return:
        """
        try:
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(output_audio_path, codec='pcm_s16le')
            print(f"音频已成功保存到 {output_audio_path}")

            os.makedirs(move_to_directory, exist_ok=True)
            video_file_name = os.path.basename(video_path)
            move_to_path = os.path.join(move_to_directory, video_file_name)
            shutil.move(video_path, move_to_path)
            print(f"成功把{video_path}转为pdf,并移到路径:{move_to_directory}")
        except ExtractAudioError as e:
            print(f"提取音频时出错: {e}")
