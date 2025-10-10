#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QImage, QCursor, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QPoint, QRect

class PreviewWidget(QWidget):
    def __init__(self, watermark_processor):
        super().__init__()
        self.watermark_processor = watermark_processor
        self.current_image = None
        self.current_image_path = None
        self.dragging = False
        self.drag_start_pos = None
        self.original_position = None
        self.scale_factor = 1.0  # 缩放因子
        self.scaled_pixmap = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建预览标签
        self.preview_label = QLabel("请导入图片")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")
        self.preview_label.setMouseTracking(True)  # 启用鼠标跟踪
        
        layout.addWidget(self.preview_label)
    
    def set_image(self, image_path):
        """设置当前预览图片"""
        self.current_image_path = image_path
        self.current_image = QImage(image_path)
        self.update_preview()
    
    def update_preview(self):
        """更新预览图像，应用水印效果"""
        if self.current_image is None:
            return
        
        # 获取预览区域大小
        preview_size = self.preview_label.size()
        
        # 创建一个副本用于预览
        preview_image = self.current_image.copy()
        
        # 应用水印
        self.watermark_processor.apply_watermark_preview(preview_image)
        
        # 缩放图像以适应预览区域
        pixmap = QPixmap.fromImage(preview_image)
        self.scaled_pixmap = pixmap.scaled(
            preview_size, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 计算缩放因子
        if pixmap.width() > 0:
            self.scale_factor = self.scaled_pixmap.width() / pixmap.width()
        
        # 显示预览
        self.preview_label.setPixmap(self.scaled_pixmap)
    
    def resizeEvent(self, event):
        """窗口大小改变时更新预览"""
        super().resizeEvent(event)
        if self.current_image:
            self.update_preview()
    
    def mousePressEvent(self, event):
        """鼠标按下事件，开始拖拽"""
        if event.button() == Qt.LeftButton and self.current_image:
            # 获取当前鼠标位置
            pos = event.pos()
            
            # 检查是否点击在水印上
            if self.watermark_processor.custom_position:
                text_rect = self.watermark_processor.get_text_rect_standalone()
                
                # 增大判定区域，在原有文本矩形的基础上向四周扩展10像素
                padding = 20  # 增大判定区域的像素值
                scaled_rect = QRect(
                    (self.watermark_processor.custom_position.x() * self.scale_factor) - padding,
                    (self.watermark_processor.custom_position.y() * self.scale_factor) - padding,
                    (text_rect.width() * self.scale_factor) + (padding * 2),
                    (text_rect.height() * self.scale_factor) + (padding * 2)
                )
                
                if scaled_rect.contains(pos):
                    self.dragging = True
                    self.drag_start_pos = pos
                    self.original_position = QPoint(
                        self.watermark_processor.custom_position.x(),
                        self.watermark_processor.custom_position.y()
                    )
                    self.setCursor(QCursor(Qt.ClosedHandCursor))
            else:
                # 如果没有自定义位置，则创建一个
                abs_pos = QPoint(
                    int(pos.x() / self.scale_factor),
                    int(pos.y() / self.scale_factor)
                )
                # 传入图像尺寸以计算相对位置
                self.watermark_processor.set_custom_position(
                    abs_pos, 
                    self.current_image.width(), 
                    self.current_image.height()
                )
                self.dragging = True
                self.drag_start_pos = pos
                self.original_position = self.watermark_processor.custom_position
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                self.update_preview()

    def mouseMoveEvent(self, event):
        """鼠标移动事件，更新拖拽位置"""
        if self.dragging and event.buttons() & Qt.LeftButton:
            # 计算偏移量
            delta = event.pos() - self.drag_start_pos
            
            # 计算新位置
            new_x = self.original_position.x() + int(delta.x() / self.scale_factor)
            new_y = self.original_position.y() + int(delta.y() / self.scale_factor)
            
            # 更新水印位置，同时更新相对位置
            self.watermark_processor.set_custom_position(
                QPoint(new_x, new_y),
                self.current_image.width(),
                self.current_image.height()
            )
            
            # 更新预览
            self.update_preview()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件，结束拖拽"""
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def get_current_position(self):
        """获取当前水印位置"""
        if not self.current_image or not self.scaled_pixmap:
            return QPoint(0, 0)
            
        # 获取水印文本的矩形区域
        # 使用watermark_processor中的字体大小
        if self.watermark_processor.custom_position:
            return self.watermark_processor.custom_position
        
        # 使用九宫格位置
        font = QFont()
        font.setPointSize(self.watermark_processor.font_size)
        
        # 不创建QPainter实例，直接使用QFontMetrics
        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(self.watermark_processor.text)
        text_width = rect.width()
        text_height = rect.height()
        
        return self.watermark_processor.position_map[self.watermark_processor.position](
            self.current_image.width(), 
            self.current_image.height(), 
            text_width, 
            text_height
        )