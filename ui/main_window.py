#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QListWidget, 
                            QListWidgetItem, QComboBox, QLineEdit, QSlider, 
                            QGroupBox, QRadioButton, QSpinBox, QColorDialog,
                            QMessageBox, QSplitter, QFrame, QGridLayout, QAction,
                            QMenu, QToolBar, QSizePolicy, QScrollArea, QCheckBox,
                            QDialog, QInputDialog)
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor, QPainter, QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QEvent, pyqtSignal, QMimeData

from core.file_handler import FileHandler
from core.watermark import WatermarkProcessor
from core.config_manager import ConfigManager
from ui.preview_widget import PreviewWidget
from ui.image_list_widget import ImageListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.watermark_processor = WatermarkProcessor()
        self.config_manager = ConfigManager()
        
        self.init_ui()
        self.setup_connections()
        self.load_templates()  # 加载所有模板
        self.load_default_config()
        
        self.setWindowTitle("水印文件本地应用")
        self.setMinimumSize(1000, 700)
        self.setAcceptDrops(True)
        self.showMaximized()  # 设置窗口启动时最大化
        
    def init_ui(self):
        # 创建主窗口布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 创建左侧图片列表区域
        self.image_list = ImageListWidget()
        
        # 创建中间预览区域
        self.preview_widget = PreviewWidget(self.watermark_processor)
        
        # 创建右侧控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        
        # 文件操作区域
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout()
        
        import_btn = QPushButton("导入图片")
        import_folder_btn = QPushButton("导入文件夹")
        export_btn = QPushButton("导出图片")
        
        file_layout.addWidget(import_btn)
        file_layout.addWidget(import_folder_btn)
        file_layout.addWidget(export_btn)
        file_group.setLayout(file_layout)
        
        # 水印设置区域
        watermark_group = QGroupBox("水印设置")
        watermark_layout = QVBoxLayout()
        
        # 文本内容
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("文本内容:"))
        self.text_input = QLineEdit("水印文本")
        text_layout.addWidget(self.text_input)
        
        # 字体设置
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体大小:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(24)
        font_layout.addWidget(self.font_size)
        
        # 颜色设置
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("字体颜色:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(24, 24)
        self.current_color = QColor(255, 0, 0, 128)  # 半透明红色
        self.update_color_button()
        color_layout.addWidget(self.color_btn)
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_value = QLabel("50%")
        opacity_layout.addWidget(self.opacity_value)
        
        # 位置设置
        position_group = QGroupBox("位置设置")
        position_layout = QGridLayout()
        
        # 九宫格位置选择
        self.position_buttons = []
        positions = [
            (0, 0, "左上"), (0, 1, "上中"), (0, 2, "右上"),
            (1, 0, "左中"), (1, 1, "中心"), (1, 2, "右中"),
            (2, 0, "左下"), (2, 1, "下中"), (2, 2, "右下")
        ]
        
        for row, col, text in positions:
            btn = QPushButton(text)
            btn.setCheckable(True)
            position_layout.addWidget(btn, row, col)
            self.position_buttons.append(btn)
        
        # 默认选中中心位置
        self.position_buttons[4].setChecked(True)
        
        position_group.setLayout(position_layout)
        
        # 模板管理
        template_group = QGroupBox("模板管理")
        template_layout = QHBoxLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("默认模板")
        save_template_btn = QPushButton("保存模板")
        delete_template_btn = QPushButton("删除模板")
        
        template_layout.addWidget(self.template_combo)
        template_layout.addWidget(save_template_btn)
        template_layout.addWidget(delete_template_btn)
        
        template_group.setLayout(template_layout)
        
        # 添加所有控件到水印设置区域
        watermark_layout.addLayout(text_layout)
        watermark_layout.addLayout(font_layout)
        watermark_layout.addLayout(color_layout)
        watermark_layout.addLayout(opacity_layout)
        watermark_layout.addWidget(position_group)
        watermark_group.setLayout(watermark_layout)
        
        # 添加所有组到控制面板
        control_layout.addWidget(file_group)
        control_layout.addWidget(watermark_group)
        control_layout.addWidget(template_group)
        control_layout.addStretch()
        
        # 创建分割器并添加三个主要区域
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_list)
        splitter.addWidget(self.preview_widget)
        splitter.addWidget(control_panel)
        
        # 设置分割器的初始大小比例
        splitter.setSizes([200, 500, 300])
        
        main_layout.addWidget(splitter)
        
        # 存储控件引用
        self.import_btn = import_btn
        self.import_folder_btn = import_folder_btn
        self.export_btn = export_btn
        self.save_template_btn = save_template_btn
        self.delete_template_btn = delete_template_btn
    
    def setup_connections(self):
        # 文件操作
        self.import_btn.clicked.connect(self.import_images)
        self.import_folder_btn.clicked.connect(self.import_folder)
        self.export_btn.clicked.connect(self.export_images)
        
        # 水印设置
        self.text_input.textChanged.connect(self.update_watermark)
        self.font_size.valueChanged.connect(self.update_watermark)
        self.color_btn.clicked.connect(self.choose_color)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        
        # 位置设置
        for i, btn in enumerate(self.position_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.set_position(idx))
        
        # 模板管理
        self.save_template_btn.clicked.connect(self.save_template)
        self.delete_template_btn.clicked.connect(self.delete_template)
        self.template_combo.currentIndexChanged.connect(self.load_template)
        
        # 图片列表
        self.image_list.currentItemChanged.connect(self.change_preview_image)
    
    def load_default_config(self):
        # 加载默认配置或上次的配置
        config = self.config_manager.load_default_config()
        if config:
            self.apply_config(config)
            # 如果是上次使用的配置，在UI中显示"上次设置"
            if os.path.exists(self.config_manager.last_config_path):
                # 查找是否有匹配的模板
                for i in range(self.template_combo.count()):
                    template_name = self.template_combo.itemText(i)
                    template_config = self.config_manager.load_template(template_name)
                    if template_config == config:
                        self.template_combo.setCurrentIndex(i)
                        break
    
    def apply_config(self, config):
        # 应用配置到UI
        if 'text' in config:
            self.text_input.setText(config['text'])
        if 'font_size' in config:
            self.font_size.setValue(config['font_size'])
        if 'color' in config:
            self.current_color = QColor(*config['color'])
            self.update_color_button()
        if 'opacity' in config:
            self.opacity_slider.setValue(config['opacity'])
            
        # 处理位置信息
        if 'custom_position' in config:
            # 优先使用自定义位置
            custom_pos = QPoint(config['custom_position'][0], config['custom_position'][1])
            self.watermark_processor.set_custom_position(custom_pos)
            # 取消所有位置按钮的选中状态
            for btn in self.position_buttons:
                btn.setChecked(False)
        elif 'relative_position' in config:
            # 使用相对位置
            self.watermark_processor.relative_position = config['relative_position']
            # 取消所有位置按钮的选中状态
            for btn in self.position_buttons:
                btn.setChecked(False)
        elif 'position' in config:
            # 使用预设位置
            for btn in self.position_buttons:
                btn.setChecked(False)
            self.position_buttons[config['position']].setChecked(True)
            # 将位置信息应用到水印处理器
            self.watermark_processor.set_position(config['position'])
    
    def update_color_button(self):
        # 更新颜色按钮的背景色
        style = f"background-color: rgba({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()}, {self.current_color.alpha()});"
        self.color_btn.setStyleSheet(style)
    
    def update_opacity(self, value):
        # 更新透明度值
        self.opacity_value.setText(f"{value}%")
        self.current_color.setAlpha(int(255 * value / 100))
        self.update_color_button()
        self.update_watermark()
    
    def choose_color(self):
        # 选择颜色
        color = QColorDialog.getColor(self.current_color, self, "选择水印颜色", QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.current_color = color
            self.update_color_button()
            # 更新透明度滑块
            self.opacity_slider.setValue(int(color.alpha() / 2.55))
            self.update_watermark()
    
    def set_position(self, position_index):
        # 设置水印位置
        for i, btn in enumerate(self.position_buttons):
            if i != position_index:
                btn.setChecked(False)
        
        # 使用九宫格位置时，清除自定义位置和相对位置
        self.watermark_processor.set_position(position_index)
        # 更新预览
        self.preview_widget.update_preview()
    
    def update_watermark(self):
        # 更新水印设置
        text = self.text_input.text()
        font_size = self.font_size.value()
        color = self.current_color
        
        self.watermark_processor.set_text(text)
        self.watermark_processor.set_font_size(font_size)
        self.watermark_processor.set_color(color)
        
        self.preview_widget.update_preview()
    
    def import_images(self):
        # 导入图片
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_paths:
            self.process_imported_files(file_paths)
    
    def import_folder(self):
        # 导入文件夹
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if folder_path:
            file_paths = self.file_handler.get_images_from_folder(folder_path)
            self.process_imported_files(file_paths)
    
    def process_imported_files(self, file_paths):
        # 处理导入的文件
        for file_path in file_paths:
            self.image_list.add_image(file_path)
        
        # 如果这是第一张图片，则显示预览
        if self.image_list.count() > 0 and self.preview_widget.current_image is None:
            self.image_list.setCurrentRow(0)
    
    def change_preview_image(self, current, previous):
        # 切换预览图片
        if current:
            image_path = current.data(Qt.UserRole)
            self.preview_widget.set_image(image_path)
    
    def export_images(self):
        # 导出图片
        if self.image_list.count() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的图片")
            return
        
        # 收集所有图片路径
        image_paths = []
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            image_path = item.data(Qt.UserRole)
            image_paths.append(image_path)
        
        # 打开导出配置对话框
        from ui.export_dialog import ExportDialog
        dialog = ExportDialog(self, image_paths)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        # 获取导出配置
        config = dialog.get_export_config()
        output_dir = config["output_dir"]
        prefix = config["prefix"]
        suffix = config["suffix"]
        format_option = config["format"]
        quality = config.get("quality", 95)  # 获取质量设置，默认95
        
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择有效的输出目录")
            return
            
        # 安全检查：检查是否导出到原图片所在文件夹
        import os
        for image_path in image_paths:
            image_dir = os.path.dirname(image_path)
            if os.path.normpath(image_dir) == os.path.normpath(output_dir):
                result = QMessageBox.warning(
                    self, 
                    "安全警告", 
                    "您正在尝试导出到原图片所在的文件夹，这可能会覆盖原图。\n是否继续？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if result == QMessageBox.No:
                    return
                break
        
        # 导出所有图片
        success_count = 0
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            image_path = item.data(Qt.UserRole)
            
            # 应用水印并保存
            success = self.watermark_processor.apply_watermark_and_save(
                image_path, output_dir, prefix, suffix, format_option
            )
            
            if success:
                success_count += 1
        
        QMessageBox.information(self, "导出完成", f"成功导出 {success_count} 张图片到 {output_dir}")
    
    def save_template(self):
        # 保存当前水印设置为模板
        template_name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        
        if ok and template_name:
            # 获取当前设置
            config = {
                'text': self.text_input.text(),
                'font_size': self.font_size.value(),
                'color': (self.current_color.red(), self.current_color.green(), 
                          self.current_color.blue(), self.current_color.alpha()),
                'opacity': self.opacity_slider.value(),
                'position': self.get_current_position_index()
            }
            
            # 保存自定义位置信息
            if self.watermark_processor.custom_position:
                config['custom_position'] = (
                    self.watermark_processor.custom_position.x(),
                    self.watermark_processor.custom_position.y()
                )
            
            # 保存相对位置信息
            if self.watermark_processor.relative_position:
                config['relative_position'] = self.watermark_processor.relative_position
            
            # 保存模板
            self.config_manager.save_template(template_name, config)
            
            # 更新模板列表
            if self.template_combo.findText(template_name) == -1:
                self.template_combo.addItem(template_name)
            
            QMessageBox.information(self, "保存成功", f"模板 '{template_name}' 已保存")
    
    def delete_template(self):
        # 删除当前选中的模板
        current_template = self.template_combo.currentText()
        
        if current_template == "默认模板":
            QMessageBox.warning(self, "警告", "无法删除默认模板")
            return
        
        reply = QMessageBox.question(self, "确认删除", 
                                     f"确定要删除模板 '{current_template}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.config_manager.delete_template(current_template)
            self.template_combo.removeItem(self.template_combo.currentIndex())
            QMessageBox.information(self, "删除成功", f"模板 '{current_template}' 已删除")
    
    def load_templates(self):
        """加载所有可用的模板到下拉列表"""
        # 清空当前列表（保留默认模板）
        while self.template_combo.count() > 1:
            self.template_combo.removeItem(1)
            
        # 获取所有模板并添加到下拉列表
        templates = self.config_manager.get_all_templates()
        for template in templates:
            if template != "默认模板" and self.template_combo.findText(template) == -1:
                self.template_combo.addItem(template)
    
    def load_template(self, index):
        # 加载选中的模板
        template_name = self.template_combo.currentText()
        
        if template_name:
            config = self.config_manager.load_template(template_name)
            if config:
                self.apply_config(config)
                self.update_watermark()
                # 保存为上次使用的配置
                self.config_manager.save_last_config(config)
    
    def get_current_position_index(self):
        # 获取当前选中的位置索引
        for i, btn in enumerate(self.position_buttons):
            if btn.isChecked():
                return i
        return 4  # 默认中心位置
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        # 拖拽进入事件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        # 拖拽放下事件
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls]
        
        # 过滤出图片文件
        image_paths = self.file_handler.filter_image_files(file_paths)
        
        if image_paths:
            self.process_imported_files(image_paths)