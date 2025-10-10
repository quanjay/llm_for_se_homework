#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QImage, QPainter, QFont, QColor
from PyQt5.QtCore import Qt, QPoint, QRect
import os

class WatermarkProcessor:
    """水印处理类，负责水印的添加和预览"""
    
    def __init__(self):
        self.text = "水印文本"
        self.font_size = 24
        self.color = QColor(255, 0, 0, 128)  # 半透明红色
        self.position = 4  # 默认中心位置
        self.custom_position = None  # 自定义位置
        self.relative_position = None  # 相对位置 (x%, y%)
        
        # 位置映射（九宫格）
        self.position_map = [
            lambda w, h, tw, th: QPoint(10, 10),  # 左上
            lambda w, h, tw, th: QPoint((w - tw) // 2, 10),  # 上中
            lambda w, h, tw, th: QPoint(w - tw - 10, 10),  # 右上
            lambda w, h, tw, th: QPoint(10, (h - th) // 2),  # 左中
            lambda w, h, tw, th: QPoint((w - tw) // 2, (h - th) // 2),  # 中心
            lambda w, h, tw, th: QPoint(w - tw - 10, (h - th) // 2),  # 右中
            lambda w, h, tw, th: QPoint(10, h - th - 10),  # 左下
            lambda w, h, tw, th: QPoint((w - tw) // 2, h - th - 10),  # 下中
            lambda w, h, tw, th: QPoint(w - tw - 10, h - th - 10),  # 右下
        ]
    
    def set_text(self, text):
        """设置水印文本"""
        self.text = text
    
    def set_font_size(self, size):
        """设置字体大小"""
        self.font_size = size
    
    def set_color(self, color):
        """设置水印颜色"""
        self.color = color
    
    def set_position(self, position_index):
        """设置水印位置"""
        if 0 <= position_index < len(self.position_map):
            self.position = position_index
            self.custom_position = None  # 清除自定义位置
            self.relative_position = None  # 清除相对位置
    
    def set_custom_position(self, position, image_width=None, image_height=None):
        """设置自定义位置，同时计算相对位置"""
        self.custom_position = position
        
        # 如果提供了图像尺寸，计算相对位置
        if image_width and image_height and position:
            rel_x = position.x() / image_width
            rel_y = position.y() / image_height
            self.relative_position = (rel_x, rel_y)
            
    def get_position_from_relative(self, image_width, image_height):
        """根据相对位置和图像尺寸计算绝对位置"""
        if self.relative_position:
            rel_x, rel_y = self.relative_position
            abs_x = int(rel_x * image_width)
            abs_y = int(rel_y * image_height)
            return QPoint(abs_x, abs_y)
        return None
    
    def get_text_rect(self, painter, image_width, image_height):
        """获取文本矩形区域"""
        # 计算文本大小
        rect = painter.fontMetrics().boundingRect(self.text)
        text_width = rect.width()
        text_height = rect.height()
        
        # 计算位置
        if self.relative_position:
            # 使用相对位置计算
            rel_x, rel_y = self.relative_position
            position = QPoint(int(rel_x * image_width), int(rel_y * image_height))
            self.custom_position = position
        elif self.custom_position:
            position = self.custom_position
        else:
            position = self.position_map[self.position](image_width, image_height, text_width, text_height)
        
        return QRect(position.x(), position.y(), text_width, text_height)
        
    def get_text_rect_standalone(self, font=None):
        """获取文本的矩形区域（独立版本，不需要QPainter实例）"""
        from PyQt5.QtGui import QFontMetrics, QFont
        if font is None:
            font = QFont()
            font.setPointSize(self.font_size)
        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(self.text)
        return rect
    
    def apply_watermark_preview(self, qimage):
        """在QImage上应用水印（用于预览）"""
        if not self.text:
            return
        
        # 创建绘图对象
        painter = QPainter(qimage)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # 设置字体
        font = QFont()
        font.setPointSize(self.font_size)
        painter.setFont(font)
        
        # 设置颜色
        painter.setPen(self.color)
        
        # 获取文本矩形区域
        image_width = qimage.width()
        image_height = qimage.height()
        text_rect = self.get_text_rect(painter, image_width, image_height)
        
        # 绘制文本
        painter.drawText(text_rect.x(), text_rect.y() + text_rect.height(), self.text)
        painter.end()
    
    def apply_watermark_and_save(self, image_path, output_dir, prefix, suffix, format_option):
        """应用水印并保存图片"""
        try:
            # 获取文件名（不含路径和扩展名）
            base_name = os.path.basename(image_path)
            file_name, _ = os.path.splitext(base_name)
            
            # 构建输出文件名
            output_file = f"{prefix}{file_name}{suffix}.{format_option.lower()}"
            output_path = os.path.join(output_dir, output_file)
            
            # 使用与预览相同的方法应用水印
            # 创建QImage
            qimage = QImage(image_path)
            if qimage.isNull():
                return False
                
            # 创建绘图对象
            painter = QPainter()
            painter.begin(qimage)
            
            # 设置字体
            font = QFont()
            font.setPointSize(self.font_size)
            painter.setFont(font)
            
            # 设置颜色
            painter.setPen(self.color)
            
            # 计算位置
            image_width = qimage.width()
            image_height = qimage.height()
            text_rect = self.get_text_rect(painter, image_width, image_height)
            
            # 绘制文本
            painter.drawText(text_rect, Qt.AlignLeft, self.text)
            
            # 结束绘图
            painter.end()
            
            # 保存图片，指定格式和质量
            if format_option.lower() == 'jpg' or format_option.lower() == 'jpeg':
                qimage.save(output_path, 'JPEG', 95)  # 95是质量参数，范围0-100
            else:  # PNG
                qimage.save(output_path, 'PNG')
                
            return True
        except Exception as e:
            print(f"导出图片时出错: {e}")
            return False