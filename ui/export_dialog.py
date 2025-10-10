#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QComboBox, QFileDialog, 
                            QGroupBox, QRadioButton, QCheckBox, QGridLayout)
from PyQt5.QtCore import Qt

class ExportDialog(QDialog):
    def __init__(self, parent=None, image_paths=None):
        super().__init__(parent)
        self.setWindowTitle("导出配置")
        self.setMinimumWidth(400)
        self.image_paths = image_paths or []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 导出路径选择
        path_group = QGroupBox("导出路径")
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output_dir)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        path_group.setLayout(path_layout)
        
        # 导出格式选择
        format_group = QGroupBox("导出格式")
        format_layout = QHBoxLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("JPEG", "jpg")
        self.format_combo.addItem("PNG", "png")
        
        format_layout.addWidget(self.format_combo)
        format_group.setLayout(format_layout)
        
        # 文件命名规则
        naming_group = QGroupBox("文件命名规则")
        naming_layout = QGridLayout()
        
        # 命名选项
        self.use_prefix_checkbox = QCheckBox("使用前缀")
        self.use_prefix_checkbox.setChecked(True)
        self.use_suffix_checkbox = QCheckBox("使用后缀")
        self.use_suffix_checkbox.setChecked(True)
        
        naming_layout.addWidget(self.use_prefix_checkbox, 0, 0)
        naming_layout.addWidget(self.use_suffix_checkbox, 1, 0)
        
        # 前缀
        self.prefix_input = QLineEdit("wm_")
        naming_layout.addWidget(QLabel("前缀:"), 0, 1)
        naming_layout.addWidget(self.prefix_input, 0, 2)
        
        # 后缀
        self.suffix_input = QLineEdit("_watermarked")
        naming_layout.addWidget(QLabel("后缀:"), 1, 1)
        naming_layout.addWidget(self.suffix_input, 1, 2)
        
        # 连接信号
        self.use_prefix_checkbox.stateChanged.connect(self.update_naming_options)
        self.use_suffix_checkbox.stateChanged.connect(self.update_naming_options)
        
        naming_group.setLayout(naming_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        # 添加所有组件到主布局
        layout.addWidget(path_group)
        layout.addWidget(format_group)
        layout.addWidget(naming_group)
        layout.addStretch()
        layout.addLayout(btn_layout)
    
    def browse_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if output_dir:
            # 检查是否与原图路径相同
            import os
            for image_path in self.image_paths:
                image_dir = os.path.dirname(image_path)
                if os.path.normpath(image_dir) == os.path.normpath(output_dir):
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self, 
                        "安全警告", 
                        "您选择的路径与原图片所在的文件夹相同，为防止覆盖原图，请选择其他路径。"
                    )
                    return
            
            self.path_input.setText(output_dir)
    
    def update_naming_options(self):
        # 根据复选框状态启用或禁用输入框
        self.prefix_input.setEnabled(self.use_prefix_checkbox.isChecked())
        self.suffix_input.setEnabled(self.use_suffix_checkbox.isChecked())
    
    def get_export_config(self):
        # 根据复选框状态决定是否使用前缀和后缀
        prefix = self.prefix_input.text() if self.use_prefix_checkbox.isChecked() else ""
        suffix = self.suffix_input.text() if self.use_suffix_checkbox.isChecked() else ""
        
        return {
            "output_dir": self.path_input.text(),
            "format": self.format_combo.currentData(),
            "prefix": prefix,
            "suffix": suffix,
            "use_prefix": self.use_prefix_checkbox.isChecked(),
            "use_suffix": self.use_suffix_checkbox.isChecked()
        }