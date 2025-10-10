#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
import os

class ImageListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setIconSize(QSize(64, 64))
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setWrapping(True)
        self.setSpacing(10)
        self.setAcceptDrops(True)
    
    def add_image(self, image_path):
        """添加图片到列表"""
        # 检查是否已存在
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == image_path:
                return
        
        # 创建缩略图
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image).scaled(
            64, 64, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 创建列表项
        item = QListWidgetItem(QIcon(pixmap), os.path.basename(image_path))
        item.setData(Qt.UserRole, image_path)
        item.setToolTip(image_path)
        
        # 添加到列表
        self.addItem(item)