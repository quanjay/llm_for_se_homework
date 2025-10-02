from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSlider, QComboBox, QPushButton, QGroupBox,
                             QRadioButton, QButtonGroup, QColorDialog, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class WatermarkPanel(QWidget):
    """水印设置面板组件"""
    
    # 自定义信号
    settings_changed = pyqtSignal()
    
    def __init__(self, watermark_processor):
        super().__init__()
        self.watermark_processor = watermark_processor
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建水印文本设置组
        text_group = QGroupBox("水印文本")
        text_layout = QVBoxLayout(text_group)
        
        # 文本输入
        text_layout.addWidget(QLabel("文本内容:"))
        self.text_edit = QLineEdit()
        self.text_edit.setText(self.watermark_processor.text)
        self.text_edit.textChanged.connect(self._on_text_changed)
        text_layout.addWidget(self.text_edit)
        
        # 字体设置
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Times New Roman", "Courier New", "SimSun", "SimHei"])
        self.font_combo.setCurrentText(self.watermark_processor.font_name)
        self.font_combo.currentTextChanged.connect(self._on_font_changed)
        font_layout.addWidget(self.font_combo)
        text_layout.addLayout(font_layout)
        
        # 字体大小
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("大小:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 100)
        self.size_slider.setValue(self.watermark_processor.font_size)
        self.size_slider.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(self.size_slider)
        self.size_label = QLabel(str(self.watermark_processor.font_size))
        size_layout.addWidget(self.size_label)
        text_layout.addLayout(size_layout)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色:"))
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 20)
        color = self.watermark_processor.font_color
        self.current_color = QColor(color[0], color[1], color[2])
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()}")
        self.color_button.clicked.connect(self._on_color_clicked)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        text_layout.addLayout(color_layout)
        
        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100 - (self.watermark_processor.font_color[3] * 100 // 255))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel(f"{self.opacity_slider.value()}%")
        opacity_layout.addWidget(self.opacity_label)
        text_layout.addLayout(opacity_layout)
        
        layout.addWidget(text_group)
        
        # 创建位置设置组
        position_group = QGroupBox("水印位置")
        position_layout = QVBoxLayout(position_group)
        
        # 预设位置
        preset_layout = QGridLayout()
        
        # 创建九宫格按钮
        self.position_buttons = {}
        positions = [
            ("topleft", 0, 0), ("topcenter", 0, 1), ("topright", 0, 2),
            ("leftcenter", 1, 0), ("center", 1, 1), ("rightcenter", 1, 2),
            ("bottomleft", 2, 0), ("bottomcenter", 2, 1), ("bottomright", 2, 2)
        ]
        
        for pos_name, row, col in positions:
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, p=pos_name: self._on_position_clicked(p))
            preset_layout.addWidget(btn, row, col)
            self.position_buttons[pos_name] = btn
        
        # 设置当前选中的位置
        current_pos = self.watermark_processor.position
        if current_pos in self.position_buttons:
            self.position_buttons[current_pos].setChecked(True)
        
        position_layout.addWidget(QLabel("预设位置:"))
        position_layout.addLayout(preset_layout)
        
        # 提示信息
        position_layout.addWidget(QLabel("提示: 在预览图上拖拽水印可自定义位置"))
        
        layout.addWidget(position_group)
        
        # 添加拉伸
        layout.addStretch()
    
    def _on_text_changed(self, text):
        """文本变化事件"""
        self.watermark_processor.set_text(text)
        self.settings_changed.emit()
    
    def _on_font_changed(self, font_name):
        """字体变化事件"""
        self.watermark_processor.set_font(font_name, self.watermark_processor.font_size)
        self.settings_changed.emit()
    
    def _on_size_changed(self, size):
        """大小变化事件"""
        self.size_label.setText(str(size))
        self.watermark_processor.set_font(self.watermark_processor.font_name, size)
        self.settings_changed.emit()
    
    def _on_color_clicked(self):
        """颜色选择事件"""
        color = QColorDialog.getColor(self.current_color, self, "选择水印颜色")
        if color.isValid():
            self.current_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            
            # 更新水印颜色
            opacity = 100 - self.opacity_slider.value()
            self.watermark_processor.set_color(
                (color.red(), color.green(), color.blue()), 
                opacity
            )
            self.settings_changed.emit()
    
    def _on_opacity_changed(self, value):
        """透明度变化事件"""
        self.opacity_label.setText(f"{value}%")
        
        # 更新水印透明度
        opacity = 100 - value
        color = self.current_color
        self.watermark_processor.set_color(
            (color.red(), color.green(), color.blue()), 
            opacity
        )
        self.settings_changed.emit()
    
    def _on_position_clicked(self, position):
        """位置选择事件"""
        # 更新所有按钮状态
        for pos, btn in self.position_buttons.items():
            btn.setChecked(pos == position)
        
        # 设置水印位置
        self.watermark_processor.set_position(position)
        self.settings_changed.emit()
    
    def get_settings(self):
        """获取当前设置"""
        color = self.current_color
        opacity = 100 - self.opacity_slider.value()
        
        return {
            "text": self.text_edit.text(),
            "font_name": self.font_combo.currentText(),
            "font_size": self.size_slider.value(),
            "font_color": [color.red(), color.green(), color.blue()],
            "opacity": opacity,
            "position": self.watermark_processor.position,
            "custom_position": self.watermark_processor.custom_position
        }
    
    def apply_settings(self, settings):
        """应用设置"""
        # 设置文本
        if "text" in settings:
            self.text_edit.setText(settings["text"])
            self.watermark_processor.set_text(settings["text"])
        
        # 设置字体
        if "font_name" in settings and "font_size" in settings:
            self.font_combo.setCurrentText(settings["font_name"])
            self.size_slider.setValue(settings["font_size"])
            self.size_label.setText(str(settings["font_size"]))
            self.watermark_processor.set_font(settings["font_name"], settings["font_size"])
        
        # 设置颜色和透明度
        if "font_color" in settings and "opacity" in settings:
            color = settings["font_color"]
            opacity = settings["opacity"]
            
            self.current_color = QColor(color[0], color[1], color[2])
            self.color_button.setStyleSheet(f"background-color: {self.current_color.name()}")
            
            self.opacity_slider.setValue(100 - opacity)
            self.opacity_label.setText(f"{100 - opacity}%")
            
            self.watermark_processor.set_color(color, opacity)
        
        # 设置位置
        if "position" in settings:
            position = settings["position"]
            
            # 更新按钮状态
            for pos, btn in self.position_buttons.items():
                btn.setChecked(pos == position)
            
            self.watermark_processor.set_position(position)
        
        # 设置自定义位置
        if "custom_position" in settings and settings["custom_position"]:
            self.watermark_processor.set_custom_position(*settings["custom_position"])
        
        # 触发更新
        self.settings_changed.emit()