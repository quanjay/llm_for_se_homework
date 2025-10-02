from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict, Any, Optional
import os

class WatermarkProcessor:
    """水印处理模块，负责添加文本水印"""
    
    def __init__(self):
        # 水印文本设置
        self.text = "水印示例"
        self.font_name = "Arial"
        self.font_size = 36
        self.font_color = (255, 255, 255, 128)  # RGBA，最后一个值为透明度
        
        # 水印位置
        self.position = "center"  # 预设位置: topleft, topright, center, bottomleft, bottomright
        self.custom_position = None  # 自定义位置 (x, y)
        
        # 字体对象
        self._font = None
        self._update_font()
    
    def set_text(self, text: str) -> None:
        """设置水印文本"""
        self.text = text
    
    def set_font(self, font_name: str, font_size: int) -> bool:
        """
        设置字体和大小
        
        Args:
            font_name: 字体名称
            font_size: 字体大小
            
        Returns:
            bool: 设置是否成功
        """
        self.font_name = font_name
        self.font_size = font_size
        return self._update_font()
    
    def set_color(self, color: Tuple[int, int, int], opacity: int) -> None:
        """
        设置字体颜色和透明度
        
        Args:
            color: RGB颜色元组 (r, g, b)
            opacity: 不透明度 (0-100)
        """
        # 将不透明度转换为alpha值 (0-255)
        alpha = int(opacity * 2.55)
        self.font_color = (color[0], color[1], color[2], alpha)
    
    def set_position(self, position: str) -> None:
        """
        设置预设位置
        
        Args:
            position: 位置名称 (topleft, topright, center, bottomleft, bottomright)
        """
        if position in ["topleft", "topright", "center", "bottomleft", "bottomright", 
                       "topcenter", "bottomcenter", "leftcenter", "rightcenter"]:
            self.position = position
            self.custom_position = None
    
    def set_custom_position(self, x: int, y: int) -> None:
        """
        设置自定义位置
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.custom_position = (x, y)
        self.position = "custom"
    
    def add_watermark(self, image: Image.Image) -> Image.Image:
        """
        添加水印到图片
        
        Args:
            image: 原图片对象
            
        Returns:
            Image.Image: 添加水印后的图片对象
        """
        # 创建一个新图像，保留原图的模式和大小
        if image.mode != 'RGBA' and 'A' not in image.mode:
            watermarked = image.convert('RGBA')
        else:
            watermarked = image.copy()
        
        # 创建绘图对象
        draw = ImageDraw.Draw(watermarked)
        
        # 确保字体已加载
        if not self._font:
            self._update_font()
            
        # 确保文本不为空
        if not self.text or len(self.text.strip()) == 0:
            self.text = "水印示例"
        
        # 计算文本大小
        try:
            # 使用getbbox方法替代已弃用的textsize方法
            if hasattr(self._font, 'getbbox'):
                bbox = self._font.getbbox(self.text)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            else:
                # 向后兼容旧版本PIL
                text_width, text_height = draw.textsize(self.text, font=self._font)
        except Exception as e:
            print(f"计算文本大小时出错: {str(e)}")
            # 估算文本大小
            text_width = self.font_size * len(self.text) * 0.7
            text_height = self.font_size * 1.5
        
        # 计算水印位置
        position = self._calculate_position(watermarked.size, (int(text_width), int(text_height)))
        
        # 绘制水印文本
        try:
            draw.text(position, self.text, font=self._font, fill=self.font_color)
        except UnicodeEncodeError:
            # 如果出现编码错误，尝试使用ASCII字符
            draw.text(position, "Watermark", font=self._font, fill=self.font_color)
        except Exception as e:
            print(f"绘制水印文本时出错: {str(e)}")
        
        return watermarked
    
    def _update_font(self) -> bool:
        """
        更新字体对象
        
        Returns:
            bool: 更新是否成功
        """
        try:
            # 使用更可靠的方式加载字体，支持中文
            # 尝试使用系统中常见的支持中文的字体
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
                "C:/Windows/Fonts/simkai.ttf",  # 楷体
                self.font_name  # 用户指定的字体名称
            ]
            
            for font_path in font_paths:
                try:
                    self._font = ImageFont.truetype(font_path, self.font_size)
                    return True
                except Exception:
                    continue
                    
            # 如果所有字体都加载失败，使用默认字体
            self._font = ImageFont.load_default()
            return True
            
        except Exception as e:
            print(f"加载字体时出错: {str(e)}")
            self._font = ImageFont.load_default()
            return False
    
    def _calculate_position(self, image_size: Tuple[int, int], text_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        计算水印位置
        
        Args:
            image_size: 图片大小 (width, height)
            text_size: 文本大小 (width, height)
            
        Returns:
            Tuple[int, int]: 水印位置坐标 (x, y)
        """
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 如果是自定义位置
        if self.position == "custom" and self.custom_position:
            return self.custom_position
        
        # 预设位置
        padding = 10  # 边距
        
        if self.position == "topleft":
            return (padding, padding)
        elif self.position == "topright":
            return (img_width - text_width - padding, padding)
        elif self.position == "bottomleft":
            return (padding, img_height - text_height - padding)
        elif self.position == "bottomright":
            return (img_width - text_width - padding, img_height - text_height - padding)
        elif self.position == "topcenter":
            return ((img_width - text_width) // 2, padding)
        elif self.position == "bottomcenter":
            return ((img_width - text_width) // 2, img_height - text_height - padding)
        elif self.position == "leftcenter":
            return (padding, (img_height - text_height) // 2)
        elif self.position == "rightcenter":
            return (img_width - text_width - padding, (img_height - text_height) // 2)
        else:  # center
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
    
    def get_preview(self, image: Image.Image) -> Image.Image:
        """
        获取添加水印后的预览图
        
        Args:
            image: 原图片对象
            
        Returns:
            Image.Image: 添加水印后的预览图
        """
        try:
            # 创建一个副本，避免修改原图
            preview = image.copy()
            
            # 确保图片是RGB模式
            if preview.mode != 'RGB' and preview.mode != 'RGBA':
                preview = preview.convert('RGB')
            
            # 创建绘图对象
            draw = ImageDraw.Draw(preview)
            
            # 确保字体已加载
            if not self._font:
                self._update_font()
            
            # 使用简单的文本和位置
            position = (20, 20)  # 左上角固定位置
            
            # 安全绘制文本
            try:
                draw.text(position, self.text or "水印示例", font=self._font, fill=self.font_color)
            except Exception:
                # 如果失败，使用默认文本
                draw.text(position, "Watermark", font=ImageFont.load_default(), fill=self.font_color)
            
            return preview
        except Exception as e:
            print(f"生成预览图时出错: {str(e)}")
            # 返回原图，不添加水印
            return image