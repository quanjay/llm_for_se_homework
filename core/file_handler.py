#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob

class FileHandler:
    """文件处理类，负责图片文件的导入和导出"""
    
    def __init__(self):
        # 支持的图片格式
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def get_images_from_folder(self, folder_path):
        """获取文件夹中的所有图片文件"""
        image_files = []
        
        # 遍历所有支持的格式
        for ext in self.supported_formats:
            pattern = os.path.join(folder_path, f'*{ext}')
            image_files.extend(glob.glob(pattern))
            
            # 不区分大小写的扩展名
            pattern = os.path.join(folder_path, f'*{ext.upper()}')
            image_files.extend(glob.glob(pattern))
        
        return image_files
    
    def filter_image_files(self, file_paths):
        """从文件路径列表中过滤出图片文件"""
        image_files = []
        
        for file_path in file_paths:
            # 检查是否是文件
            if os.path.isfile(file_path):
                # 检查扩展名
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.supported_formats:
                    image_files.append(file_path)
            # 检查是否是目录
            elif os.path.isdir(file_path):
                # 递归获取目录中的图片
                image_files.extend(self.get_images_from_folder(file_path))
        
        return image_files
    
    def generate_output_path(self, image_path, output_dir, prefix, suffix, format_option):
        """生成输出文件路径"""
        # 获取原文件名（不含扩展名）
        base_name = os.path.basename(image_path)
        name_without_ext = os.path.splitext(base_name)[0]
        
        # 构建新文件名
        new_name = f"{prefix}{name_without_ext}{suffix}.{format_option}"
        
        # 构建完整输出路径
        output_path = os.path.join(output_dir, new_name)
        
        return output_path