#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
水印文件本地应用主程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    """主程序入口函数"""
    # 确保资源目录存在
    for directory in ['resources', 'templates']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    app.setApplicationName("水印文件应用")
    app.setOrganizationName("WatermarkApp")
    
    # 设置应用图标（如果存在）
    icon_path = os.path.join('resources', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建并显示主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()