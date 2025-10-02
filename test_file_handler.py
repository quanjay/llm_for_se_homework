#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试文件处理功能模块
"""

import os
import sys
from core.file_handler import FileHandler

def test_file_handler():
    """测试FileHandler类的基本功能"""
    # 创建FileHandler实例
    handler = FileHandler()
    
    # 测试支持的格式
    from core.file_handler import SUPPORTED_FORMATS
    print("支持的格式:", SUPPORTED_FORMATS)
    
    # 测试格式验证
    test_files = [
        "test.jpg", "test.jpeg", "test.png", "test.bmp", "test.gif", "test.tiff", "test.txt"
    ]
    
    print("\n格式验证测试:")# 测试格式验证
    for file in test_files:
        is_valid = handler._is_supported_format(file)
        print(f"{file}: {'有效' if is_valid else '无效'}")
    
    print("\n文件处理功能测试完成")

if __name__ == "__main__":
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 运行测试
    test_file_handler()