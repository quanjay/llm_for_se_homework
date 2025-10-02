from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QListWidget, QListWidgetItem,
                             QComboBox, QLineEdit, QSlider, QGroupBox, QRadioButton,
                             QMessageBox, QAction, QMenu, QToolBar, QStatusBar, QSplitter)
from PyQt5.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QMimeData, QUrl

import os
import sys
from PIL import Image, ImageQt

# 导入核心模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.file_handler import FileHandler
from core.watermark import WatermarkProcessor
from core.config_manager import ConfigManager

from ui.image_list import ImageListWidget
from ui.preview_panel import PreviewPanel
from ui.watermark_panel import WatermarkPanel

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化核心模块
        self.file_handler = FileHandler()
        self.watermark_processor = WatermarkProcessor()
        self.config_manager = ConfigManager()
        
        # 设置窗口属性
        self.setWindowTitle("水印文件本地应用")
        self.setMinimumSize(1000, 700)
        
        # 设置接受拖放
        self.setAcceptDrops(True)
        
        # 创建UI
        self._create_ui()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        
        # 加载上次配置
        self.config_manager.load_last_config()
        self._apply_config()
        
        # 连接信号和槽
        self._connect_signals()
    
    def _create_ui(self):
        """创建主界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：图片列表
        self.image_list = ImageListWidget(self.file_handler)
        splitter.addWidget(self.image_list)
        
        # 中间：预览面板
        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)
        
        # 右侧：水印设置面板
        self.watermark_panel = WatermarkPanel(self.watermark_processor)
        splitter.addWidget(self.watermark_panel)
        
        # 设置分割器比例
        splitter.setSizes([200, 500, 300])
    
    def _create_menu(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        # 导入图片
        import_action = QAction("导入图片", self)
        import_action.triggered.connect(self._import_images)
        file_menu.addAction(import_action)
        
        # 导入文件夹
        import_dir_action = QAction("导入文件夹", self)
        import_dir_action.triggered.connect(self._import_directory)
        file_menu.addAction(import_dir_action)
        
        file_menu.addSeparator()
        
        # 导出图片
        export_action = QAction("导出图片", self)
        export_action.triggered.connect(self._export_images)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 模板菜单
        template_menu = self.menuBar().addMenu("模板")
        
        # 保存模板
        save_template_action = QAction("保存当前设置为模板", self)
        save_template_action.triggered.connect(self._save_template)
        template_menu.addAction(save_template_action)
        
        # 加载模板
        load_template_action = QAction("加载模板", self)
        load_template_action.triggered.connect(self._load_template)
        template_menu.addAction(load_template_action)
        
        # 管理模板
        manage_template_action = QAction("管理模板", self)
        manage_template_action.triggered.connect(self._manage_templates)
        template_menu.addAction(manage_template_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 导入图片
        import_action = QAction("导入图片", self)
        import_action.triggered.connect(self._import_images)
        toolbar.addAction(import_action)
        
        # 导出图片
        export_action = QAction("导出图片", self)
        export_action.triggered.connect(self._export_images)
        toolbar.addAction(export_action)
    
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 图片列表选择变化
        self.image_list.currentItemChanged.connect(self._update_preview)
        
        # 水印设置变化
        self.watermark_panel.settings_changed.connect(self._update_preview)
    
    def _import_images(self):
        """导入图片"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
        )
        
        if file_paths:
            success, total = self.file_handler.import_images(file_paths)
            self.statusBar.showMessage(f"成功导入 {success}/{total} 张图片")
            self.image_list.refresh_list()
    
    def _import_directory(self):
        """导入文件夹"""
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if directory:
            success, total = self.file_handler.import_directory(directory)
            self.statusBar.showMessage(f"成功导入 {success}/{total} 张图片")
            self.image_list.refresh_list()
    
    def _export_images(self):
        """导出图片"""
        # 检查是否有导入的图片
        if not self.file_handler.get_imported_images():
            QMessageBox.warning(self, "警告", "没有可导出的图片")
            return
        
        # 选择输出目录
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not directory:
            return
        
        # 设置输出目录
        if not self.file_handler.set_output_directory(directory):
            QMessageBox.critical(self, "错误", "无法设置输出目录")
            return
        
        # 处理所有图片并导出
        watermarked_images = {}
        for image_info in self.file_handler.get_imported_images():
            try:
                with Image.open(image_info["path"]) as img:
                    watermarked = self.watermark_processor.add_watermark(img)
                    watermarked_images[image_info["path"]] = watermarked
            except Exception as e:
                QMessageBox.warning(self, "警告", f"处理图片时出错: {str(e)}")
        
        # 导出图片
        success, total = self.file_handler.export_all_images(watermarked_images)
        
        # 显示结果
        QMessageBox.information(self, "导出完成", f"成功导出 {success}/{total} 张图片")
        self.statusBar.showMessage(f"成功导出 {success}/{total} 张图片")
    
    def _update_preview(self):
        """更新预览"""
        # 获取当前选中的图片
        current_item = self.image_list.currentItem()
        if not current_item:
            self.preview_panel.clear_preview()
            return
        
        # 获取图片路径
        image_path = current_item.data(Qt.UserRole)
        
        try:
            # 直接使用QPixmap加载图片用于预览
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 调整大小以适应预览区域
                pixmap = pixmap.scaled(
                    self.preview_panel.preview_label.width(),
                    self.preview_panel.preview_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                # 直接设置预览图片
                self.preview_panel.preview_label.setPixmap(pixmap)
                # 更新状态栏
                self.statusBar.showMessage(f"已加载图片: {os.path.basename(image_path)}")
                return
                
            # 如果QPixmap加载失败，尝试使用PIL
            # 使用PIL打开图片
            with Image.open(image_path) as img:
                # 确保图片是RGB模式
                if img.mode != 'RGB' and img.mode != 'RGBA':
                    img = img.convert('RGB')
                
                # 添加水印
                watermarked = self.watermark_processor.add_watermark(img.copy())
                
                # 更新预览
                self.preview_panel.set_preview(watermarked)
                
                # 更新状态栏
                self.statusBar.showMessage(f"已加载图片: {os.path.basename(image_path)}")
            
        except UnicodeEncodeError:
            # 特别处理编码错误
            self.statusBar.showMessage("预览图片时出现编码错误，请检查水印文本")
            self.preview_panel.clear_preview()
        except Exception as e:
            self.statusBar.showMessage(f"预览图片时出错: {str(e)}")
            self.preview_panel.clear_preview()
    
    def _save_template(self):
        """保存当前设置为模板"""
        # 获取模板名称
        name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        if not ok or not name:
            return
        
        # 更新当前配置
        self._update_config()
        
        # 保存模板
        if self.config_manager.save_template(name):
            QMessageBox.information(self, "成功", f"模板 '{name}' 保存成功")
        else:
            QMessageBox.warning(self, "警告", f"保存模板 '{name}' 失败")
    
    def _load_template(self):
        """加载模板"""
        # 获取模板列表
        templates = self.config_manager.get_template_list()
        if not templates:
            QMessageBox.information(self, "提示", "没有可用的模板")
            return
        
        # 选择模板
        template, ok = QInputDialog.getItem(self, "加载模板", "请选择模板:", templates, 0, False)
        if not ok or not template:
            return
        
        # 加载模板
        if self.config_manager.load_template(template):
            # 应用配置
            self._apply_config()
            QMessageBox.information(self, "成功", f"模板 '{template}' 加载成功")
        else:
            QMessageBox.warning(self, "警告", f"加载模板 '{template}' 失败")
    
    def _manage_templates(self):
        """管理模板"""
        # 获取模板列表
        templates = self.config_manager.get_template_list()
        if not templates:
            QMessageBox.information(self, "提示", "没有可用的模板")
            return
        
        # 选择要删除的模板
        template, ok = QInputDialog.getItem(self, "删除模板", "请选择要删除的模板:", templates, 0, False)
        if not ok or not template:
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", f"确定要删除模板 '{template}' 吗?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        # 删除模板
        if self.config_manager.delete_template(template):
            QMessageBox.information(self, "成功", f"模板 '{template}' 删除成功")
        else:
            QMessageBox.warning(self, "警告", f"删除模板 '{template}' 失败")
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "水印文件本地应用\n\n版本: 1.0\n\n一款简单易用的本地水印应用程序")
    
    def _update_config(self):
        """更新当前配置"""
        # 获取水印设置
        watermark_settings = self.watermark_panel.get_settings()
        
        # 获取导出设置
        export_settings = {
            "format": self.file_handler.output_format,
            "naming_rule": self.file_handler.naming_rule
        }
        
        # 更新配置
        config = {
            "watermark": watermark_settings,
            "export": export_settings
        }
        self.config_manager.set_current_config(config)
    
    def _apply_config(self):
        """应用当前配置"""
        config = self.config_manager.get_current_config()
        
        # 应用水印设置
        if "watermark" in config:
            self.watermark_panel.apply_settings(config["watermark"])
        
        # 应用导出设置
        if "export" in config:
            export_config = config["export"]
            if "format" in export_config:
                self.file_handler.set_output_format(export_config["format"])
            if "naming_rule" in export_config:
                rule = export_config["naming_rule"]
                if rule["type"] == "prefix":
                    self.file_handler.set_naming_rule("prefix", rule["prefix"])
                elif rule["type"] == "suffix":
                    self.file_handler.set_naming_rule("suffix", rule["suffix"])
                else:
                    self.file_handler.set_naming_rule("original")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        urls = event.mimeData().urls()
        file_paths = []
        directories = []
        
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                file_paths.append(path)
            elif os.path.isdir(path):
                directories.append(path)
        
        # 导入文件
        if file_paths:
            success, total = self.file_handler.import_images(file_paths)
            self.statusBar.showMessage(f"成功导入 {success}/{total} 张图片")
        
        # 导入目录
        for directory in directories:
            success, total = self.file_handler.import_directory(directory)
            self.statusBar.showMessage(f"成功导入 {success}/{total} 张图片")
        
        # 刷新列表
        self.image_list.refresh_list()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 保存当前配置
        self._update_config()
        self.config_manager.save_last_config()
        event.accept()