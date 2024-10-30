"""
# File       : page_layout.py
# Time       ：2024/10/14 16:50
# Author     ：jianbang
# version    ：python 3.10
# company    : IFLYTEK Co.,Ltd.
# emil       : whdx072018@foxmail.com
# Description：
"""

class LayoutAnalyzer:
    def __init__(self):
        """
        初始化 LayoutAnalyzer 类，接收一个文档的字典结构。
        """
        self.description="检查文本页面的布局是否复杂！"

    def set_document_text(self,content_lst):
        """
        :param content_lst:
        :return:
        """
        self.document=content_lst

    def get_max_depth(self, content, depth=1):
        """
        :param content:
        :param depth:
        :return:
        """
        if not isinstance(content, list):
            return depth

        depths = [
            self.get_max_depth(item['content'], depth + 1)
            for item in content
            if isinstance(item, dict) and 'content' in item
        ]

        return max(depths) if depths else depth

    def count_regions(self, content=None):
        """
        :param content:
        :return:
        """
        if content is None:
            content = self.document

        region_count = 0

        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'region':
                    region_count += 1
                if 'content' in item:
                    region_count += self.count_regions(item['content'])
            elif isinstance(item, list):
                region_count += self.count_regions(item)

        return region_count

    def count_text_blocks(self, content=None):
        """
        :param content:
        :return:
        """
        if content is None:
            content = self.document

        text_block_count = 0

        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text_block':
                    text_block_count += 1
                if 'content' in item:
                    text_block_count += self.count_text_blocks(item['content'])
            elif isinstance(item, list):
                text_block_count += self.count_text_blocks(item)

        return text_block_count

    def has_mixed_directions(self, content=None):
        """
        :param content:
        :return:
        """
        if content is None:
            content = self.document

        directions = set()

        for item in content:
            if isinstance(item, dict) and 'direction' in item:
                directions.add(item['direction'])
            elif isinstance(item, list):
                if self.has_mixed_directions(item):
                    return True

        return len(directions) > 1

    def is_block_complex_layout(self, block_content) -> bool:
        """
        :param block_content:
        :return:
        """
        max_depth = self.get_max_depth(block_content)
        region_count = self.count_regions(block_content)
        text_block_count = self.count_text_blocks(block_content)
        mixed_directions = self.has_mixed_directions(block_content)

        # 根据规则判断复杂性
        if max_depth > 2 and region_count > 3:
            if text_block_count > 10 or mixed_directions:
                return True
            else:
                return False
        return False

    def is_page_layout_complex(self):
        """
        判断页面是否具有复杂布局。
        """
        for block in self.document:
            if self.is_block_complex_layout(block['content']):
                return True
        return False

    def is_file_layout_complex(self,file_type):
        """
        :param file_type:
        :return:
        """
        if file_type=="pptx":
            return True
        else:
            return False




