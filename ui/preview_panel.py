from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageQt

class PreviewPanel(QWidget):
    """预览面板组件"""
    
    def __init__(self):
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建预览标签
        self.preview_label = QLabel("请选择图片")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f5f5f5;")
        
        # 添加到布局
        layout.addWidget(self.preview_label)
    
    def set_preview(self, image: Image.Image):
        """
        设置预览图片
        
        Args:
            image: PIL图片对象
        """
        if not image:
            self.clear_preview()
            return
        
        try:
            # 确保图片是RGB模式
            if image.mode != 'RGB' and image.mode != 'RGBA':
                image = image.convert('RGB')
                
            # 转换为QPixmap
            qimage = ImageQt.ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
            
            # 调整大小以适应预览区域
            pixmap = pixmap.scaled(
                self.preview_label.width(), 
                self.preview_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # 设置预览图片
            self.preview_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"设置预览图片时出错: {str(e)}")
            self.clear_preview()
    
    def set_pixmap(self, pixmap: QPixmap):
        """
        直接设置QPixmap预览图片（性能更好）
        
        Args:
            pixmap: QPixmap对象
        """
        if pixmap and not pixmap.isNull():
            # 调整大小以适应预览区域
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width(), 
                self.preview_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setText("")
        else:
            self.clear_preview()
    
    def clear_preview(self):
        """清除预览"""
        self.preview_label.setText("请选择图片")
        self.preview_label.setPixmap(QPixmap())  # 清除图片
    
    def resizeEvent(self, event):
        """调整大小事件"""
        # 如果有预览图片，调整其大小
        if not self.preview_label.text():
            pixmap = self.preview_label.pixmap()
            if pixmap:
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
        
        super().resizeEvent(event)