# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : ai_config.py
# Time       ：2024/10/7 14:14
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""



class OCRConfig(object):
    def __init__(self):
        """
        markdown_element_option: 默认为空字符串，所有要素均输出；针对每个要素有特殊需求时可使用本参数进行设定，输入格式为: “element_name1=value1,element_name2=value2”其中element_name可选值有：seal:印章，information_bar:信息栏，fingerprint:手印，qrcode:二维码，watermark:水印，barcode:条形码，page_header:页眉 ，page_footer:页脚，page_number:页码，layout:版面，title:标题，region:区域，paragraph:段落，textline:文本行，table:表格，graph:插图，list:列表，pseudocode:伪代码，code:代码，footnote:脚注，formula:公式；value值可选值有：0:不输出，1:输出，默认值；说明：当element_name为table时，1表示同时识别有线表和少线表，2表示只识别有线表。 string 最小长度:0, 最大长度:1000 否 watermark=0,page_header=0,page_footer=0,page_number=0,graph=0
        sed_element_option: 默认为空字符串，所有要素均输出；针对每个要素有特殊需求时可使用本参数进行设定，输入格式为:“element_name1=value1,element_name2=value2”其中element_name可选值有：seal:印章，information_bar:信息栏，fingerprint:手印，qrcode:二维码，watermark:水印，barcode:条形码，page_header:页眉，page_footer:页脚，page_number:页码，layout:版面，title:标题，region:区域，paragraph:段落，textline:文本行，table:表格，graph:插图，list:列表，pseudocode:伪代码，code:代码，footnote:脚注，formula:公式；value值可选值有：0:不输出，1:输出，默认值；说明：当element_name为table时，1表示同时识别有线表和少线表，2表示只识别有线表。
        """
        self.ocr_model_url="wss://XXXXXXXXXXXXXXXXXXXXXXXX"
        self.markdown_element_option= "watermark=0,page_header=0,page_footer=0,page_number=0,graph=0,formula=1,footnote=1,layout=1,seal=1"
        self.sed_element_option= "watermark=0,page_header=0,page_footer=0,page_number=0,graph=0,formula=1,footnote=1,layout=1,seal=1"







class VQAConfig(object):
    def __init__(self):
        self.ppt_prompt="""你是PPT信息提取专家，你的目标是客观描述PPT页面内容，以提取PPT页面的信息。
        
## 任务要求
1. 宏观理解：全面把握PPT页面内容，确保深入理解所有文本段落及其信息；
2. 流程解读：若有流程图，仔细分析流程图，关注箭头方向和步骤之间的交互，确保理解每个环节的逻辑关系；
3. 模块分析：详细描述每个文字和图像模块的具体内容，避免讨论页面布局，必须专注于模块信息；
4. 逻辑整合：确保生成的内容具有连贯性，将信息整合为流畅的描述性段落，忠于原文；
5. 直接描述：避免使用“这页PPT”,“这是关于”等措辞，直接进行内容描述，不进行总结或评述；"""
        self.vqa_model_url="ws://XXXXXXXXXXXXXXXXXXXXXXXXXX"





















