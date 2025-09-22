#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片EXIF时间水印添加工具
根据PRD.txt需求开发的命令行程序，用于读取图片EXIF信息中的拍摄时间，
并将其作为水印添加到图片上。
"""

import os
import sys
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ExifTags
import glob

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='图片EXIF时间水印添加工具')
    parser.add_argument('image_dir', help='图片目录路径')
    parser.add_argument('--size', type=int, default=20, help='水印字体大小 (默认: 20)')
    parser.add_argument('--color', default='white', help='水印颜色 (默认: white)')
    parser.add_argument('--position', default='bottom-right', 
                        choices=['top-left', 'top-center', 'top-right', 
                                'center-left', 'center', 'center-right',
                                'bottom-left', 'bottom-center', 'bottom-right'],
                        help='水印位置 (默认: bottom-right)')
    
    return parser.parse_args()

def validate_directory(directory):
    """验证目录是否存在"""
    if not os.path.exists(directory):
        print(f"错误: 目录 '{directory}' 不存在")
        return False
    
    if not os.path.isdir(directory):
        print(f"错误: '{directory}' 不是一个目录")
        return False
    
    return True

def get_image_files(directory):
    """获取目录下所有图片文件"""
    # 支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.bmp']
    
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
        image_files.extend(glob.glob(os.path.join(directory, ext.upper())))
    
    return image_files

def extract_exif_date(image_path):
    """从图片中提取EXIF拍摄日期"""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            
            if not exif_data:
                return None
            
            # 查找日期时间原始数据标签
            date_time = None
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    date_time = value
                    break
            
            if not date_time:
                return None
            
            # 解析日期时间格式 (通常格式为 "YYYY:MM:DD HH:MM:SS")
            try:
                dt = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
                return dt.strftime('%Y-%m-%d')  # 只返回年月日
            except ValueError:
                return None
    
    except Exception as e:
        print(f"提取EXIF信息时出错 ({image_path}): {str(e)}")
        return None

def get_watermark_position(position, img_width, img_height, text_width, text_height, padding=10):
    """根据指定位置计算水印坐标"""
    positions = {
        'top-left': (padding, padding),
        'top-center': ((img_width - text_width) // 2, padding),
        'top-right': (img_width - text_width - padding, padding),
        'center-left': (padding, (img_height - text_height) // 2),
        'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
        'center-right': (img_width - text_width - padding, (img_height - text_height) // 2),
        'bottom-left': (padding, img_height - text_height - padding),
        'bottom-center': ((img_width - text_width) // 2, img_height - text_height - padding),
        'bottom-right': (img_width - text_width - padding, img_height - text_height - padding)
    }
    
    return positions.get(position, positions['bottom-right'])

def add_watermark(image_path, date_text, font_size, color, position):
    """添加水印到图片"""
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # 如果找不到指定字体，使用默认字体
            font = ImageFont.load_default()
        
        # 获取文本大小
        # 使用textbbox代替已弃用的textsize方法
        left, top, right, bottom = draw.textbbox((0, 0), date_text, font=font)
        text_width = right - left
        text_height = bottom - top
        
        # 计算水印位置
        x, y = get_watermark_position(position, img.width, img.height, text_width, text_height)
        
        # 添加文本阴影以增强可读性（如果背景色与水印色相近）
        shadow_color = "black" if color != "black" else "white"
        draw.text((x+1, y+1), date_text, font=font, fill=shadow_color)
        
        # 添加水印文本
        draw.text((x, y), date_text, font=font, fill=color)
        
        return img
    
    except Exception as e:
        print(f"添加水印时出错 ({image_path}): {str(e)}")
        return None

def save_image(img, original_path, output_dir):
    """保存图片到输出目录"""
    if img is None:
        return False
    
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取原始文件名
        filename = os.path.basename(original_path)
        
        # 构建输出路径
        output_path = os.path.join(output_dir, filename)
        
        # 保存图片
        img.save(output_path, quality=95)  # 保持高质量
        return True
    
    except Exception as e:
        print(f"保存图片时出错 ({original_path}): {str(e)}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 验证目录
    if not validate_directory(args.image_dir):
        sys.exit(1)
    
    # 获取图片文件列表
    image_files = get_image_files(args.image_dir)
    
    if not image_files:
        print(f"在目录 '{args.image_dir}' 中未找到图片文件")
        sys.exit(1)
    
    # 创建输出目录
    dir_name = os.path.basename(os.path.normpath(args.image_dir))
    output_dir = os.path.join(args.image_dir, f"{dir_name}_watermark")
    
    # 处理每个图片
    total_images = len(image_files)
    successful = 0
    
    print(f"开始处理 {total_images} 张图片...")
    
    for i, image_path in enumerate(image_files, 1):
        print(f"处理图片 {i}/{total_images}: {os.path.basename(image_path)}")
        
        # 提取EXIF日期
        date_text = extract_exif_date(image_path)
        
        if not date_text:
            print(f"  警告: 无法从图片中提取拍摄日期，跳过此图片")
            continue
        
        # 添加水印
        watermarked_img = add_watermark(image_path, date_text, args.size, args.color, args.position)
        
        # 保存图片
        if watermarked_img and save_image(watermarked_img, image_path, output_dir):
            successful += 1
    
    # 输出处理结果
    print(f"\n处理完成: {successful}/{total_images} 张图片成功添加水印")
    print(f"水印图片已保存到: {output_dir}")

if __name__ == "__main__":
    main()