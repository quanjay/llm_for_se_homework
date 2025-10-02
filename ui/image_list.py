from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageQt
import os
import gc

class ImageListWidget(QListWidget):
    """图片列表组件"""
    
    def __init__(self, file_handler):
        super().__init__()
        self.file_handler = file_handler
        self.pixmap_cache = {}  # 缓存QPixmap对象
        
        # 设置列表属性
        self.setIconSize(QSize(80, 80))
        self.setResizeMode(QListWidget.Adjust)
        self.setViewMode(QListWidget.IconMode)
        self.setSpacing(10)
        self.setAcceptDrops(True)
        self.setDragEnabled(False)
    
    def refresh_list(self):
        """刷新图片列表"""
        self.clear()
        self.pixmap_cache.clear()  # 清空缓存
        gc.collect()  # 强制垃圾回收
        
        # 获取已导入的图片
        images = self.file_handler.get_imported_images()
        
        for image_info in images:
            image_path = image_info["path"]
            
            try:
                # 直接使用QPixmap加载图片
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # 缩放到合适大小
                    pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # 缓存QPixmap对象
                    self.pixmap_cache[image_path] = pixmap
                    
                    # 创建列表项
                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    item.setText(os.path.basename(image_path))
                    item.setData(Qt.UserRole, image_path)
                    
                    # 添加到列表
                    self.addItem(item)
                    continue
            except Exception:
                pass
                
            # 如果QPixmap加载失败，回退到使用PIL
            try:
                # 获取缩略图
                with Image.open(image_path) as img:
                    # 创建缩略图
                    img.thumbnail((80, 80))
                    
                    # 确保图片是RGB模式
                    if img.mode != 'RGB' and img.mode != 'RGBA':
                        img = img.convert('RGB')
                    
                    # 转换为QPixmap
                    qimage = ImageQt.ImageQt(img)
                    pixmap = QPixmap.fromImage(qimage)
                    
                    # 缓存QPixmap对象
                    self.pixmap_cache[image_path] = pixmap
                    
                    # 创建列表项
                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    item.setText(os.path.basename(image_path))
                    item.setData(Qt.UserRole, image_path)
                    
                    # 添加到列表
                    self.addItem(item)
            except Exception as e:
                print(f"无法加载图片缩略图: {image_path}, 错误: {str(e)}")
        
        # 选择第一项
        if self.count() > 0:
            self.setCurrentRow(0)