import os
import shutil
from PIL import Image
from typing import List, Tuple, Optional, Dict, Any

# 支持的图片格式
SUPPORTED_FORMATS = {
    'JPEG': ['.jpg', '.jpeg', '.jpe'],
    'PNG': ['.png'],
    'BMP': ['.bmp'],
    'TIFF': ['.tif', '.tiff']
}

# 扁平化支持的扩展名列表，用于快速检查
SUPPORTED_EXTENSIONS = [ext for formats in SUPPORTED_FORMATS.values() for ext in formats]

class FileHandler:
    """文件处理模块，负责图片的导入、格式验证和导出"""
    
    def __init__(self):
        self.imported_images: List[Dict[str, Any]] = []  # 存储导入的图片信息
        self.output_directory: str = ""  # 输出目录
        self.output_format: str = "JPEG"  # 默认输出格式
        self.naming_rule: Dict[str, Any] = {
            "type": "original",  # original, prefix, suffix
            "prefix": "",
            "suffix": ""
        }
    
    def import_image(self, file_path: str) -> bool:
        """
        导入单张图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 导入是否成功
        """
        if not os.path.isfile(file_path):
            print(f"错误: 文件不存在 - {file_path}")
            return False
            
        # 检查文件格式
        if not self._is_supported_format(file_path):
            print(f"错误: 不支持的文件格式 - {file_path}")
            return False
            
        try:
            # 打开图片验证其完整性
            with Image.open(file_path) as img:
                # 获取图片基本信息
                image_info = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode
                }
                
                # 检查是否已导入
                for existing in self.imported_images:
                    if existing["path"] == file_path:
                        return True  # 已导入，不重复添加
                
                # 添加到导入列表
                self.imported_images.append(image_info)
                print(f"成功导入图片: {file_path}")
                return True
                
        except Exception as e:
            print(f"导入图片时出错: {str(e)}")
            return False
    
    def import_images(self, file_paths: List[str]) -> Tuple[int, int]:
        """
        批量导入图片
        
        Args:
            file_paths: 图片文件路径列表
            
        Returns:
            Tuple[int, int]: (成功导入数量, 总数量)
        """
        success_count = 0
        total_count = len(file_paths)
        
        for file_path in file_paths:
            if self.import_image(file_path):
                success_count += 1
                
        return success_count, total_count
    
    def import_directory(self, directory_path: str) -> Tuple[int, int]:
        """
        导入整个目录中的图片
        
        Args:
            directory_path: 目录路径
            
        Returns:
            Tuple[int, int]: (成功导入数量, 总数量)
        """
        if not os.path.isdir(directory_path):
            print(f"错误: 目录不存在 - {directory_path}")
            return 0, 0
            
        file_paths = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_supported_format(file_path):
                    file_paths.append(file_path)
        
        return self.import_images(file_paths)
    
    def set_output_directory(self, directory: str) -> bool:
        """
        设置输出目录
        
        Args:
            directory: 输出目录路径
            
        Returns:
            bool: 设置是否成功
        """
        # 检查目录是否存在，不存在则创建
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                print(f"创建输出目录失败: {str(e)}")
                return False
        
        self.output_directory = directory
        return True
    
    def set_output_format(self, format_name: str) -> bool:
        """
        设置输出格式
        
        Args:
            format_name: 格式名称 ("JPEG" 或 "PNG")
            
        Returns:
            bool: 设置是否成功
        """
        if format_name not in ["JPEG", "PNG"]:
            print(f"错误: 不支持的输出格式 - {format_name}")
            return False
            
        self.output_format = format_name
        return True
    
    def set_naming_rule(self, rule_type: str, value: str = "") -> bool:
        """
        设置文件命名规则
        
        Args:
            rule_type: 规则类型 ("original", "prefix", "suffix")
            value: 前缀或后缀值
            
        Returns:
            bool: 设置是否成功
        """
        if rule_type not in ["original", "prefix", "suffix"]:
            print(f"错误: 不支持的命名规则 - {rule_type}")
            return False
            
        self.naming_rule = {
            "type": rule_type,
            "prefix": value if rule_type == "prefix" else "",
            "suffix": value if rule_type == "suffix" else ""
        }
        return True
    
    def export_image(self, image_path: str, watermarked_image: Image.Image) -> Optional[str]:
        """
        导出单张图片
        
        Args:
            image_path: 原图片路径
            watermarked_image: 添加水印后的图片对象
            
        Returns:
            Optional[str]: 导出的文件路径，失败则返回None
        """
        if not self.output_directory:
            print("错误: 未设置输出目录")
            return None
            
        # 安全措施：检查输出目录是否与原图片目录相同
        original_dir = os.path.dirname(image_path)
        if os.path.abspath(original_dir) == os.path.abspath(self.output_directory):
            print("错误: 输出目录不能与原图片目录相同，以防止覆盖原图")
            return None
            
        # 生成输出文件名
        original_filename = os.path.basename(image_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        
        if self.naming_rule["type"] == "original":
            output_filename = filename_without_ext
        elif self.naming_rule["type"] == "prefix":
            output_filename = f"{self.naming_rule['prefix']}{filename_without_ext}"
        else:  # suffix
            output_filename = f"{filename_without_ext}{self.naming_rule['suffix']}"
            
        # 添加扩展名
        if self.output_format == "JPEG":
            output_filename += ".jpg"
        else:  # PNG
            output_filename += ".png"
            
        output_path = os.path.join(self.output_directory, output_filename)
        
        try:
            # 保存图片
            if self.output_format == "JPEG":
                # 如果原图有透明通道，需要处理
                if watermarked_image.mode == 'RGBA':
                    # 创建白色背景
                    background = Image.new('RGB', watermarked_image.size, (255, 255, 255))
                    # 将原图合成到白色背景上
                    background.paste(watermarked_image, mask=watermarked_image.split()[3])
                    background.save(output_path, 'JPEG', quality=95)
                else:
                    watermarked_image.save(output_path, 'JPEG', quality=95)
            else:  # PNG
                watermarked_image.save(output_path, 'PNG')
                
            print(f"成功导出图片: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"导出图片时出错: {str(e)}")
            return None
    
    def export_all_images(self, watermarked_images: Dict[str, Image.Image]) -> Tuple[int, int]:
        """
        批量导出所有图片
        
        Args:
            watermarked_images: 字典，键为原图路径，值为添加水印后的图片对象
            
        Returns:
            Tuple[int, int]: (成功导出数量, 总数量)
        """
        success_count = 0
        total_count = len(watermarked_images)
        
        for original_path, watermarked_image in watermarked_images.items():
            if self.export_image(original_path, watermarked_image):
                success_count += 1
                
        return success_count, total_count
    
    def get_imported_images(self) -> List[Dict[str, Any]]:
        """获取已导入的图片列表"""
        return self.imported_images
    
    def clear_imported_images(self) -> None:
        """清空已导入的图片列表"""
        self.imported_images = []
    
    def _is_supported_format(self, file_path: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in SUPPORTED_EXTENSIONS
    
    def get_thumbnail(self, image_path: str, size: Tuple[int, int] = (100, 100)) -> Optional[Image.Image]:
        """
        获取图片缩略图
        
        Args:
            image_path: 图片路径
            size: 缩略图大小
            
        Returns:
            Optional[Image.Image]: 缩略图对象，失败则返回None
        """
        try:
            with Image.open(image_path) as img:
                # 创建缩略图
                img.thumbnail(size)
                return img.copy()
        except Exception as e:
            print(f"生成缩略图时出错: {str(e)}")
            return None