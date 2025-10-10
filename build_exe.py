#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打包脚本 - 使用PyInstaller将应用程序打包为exe文件
"""

import os
import shutil
import subprocess
import sys

def clean_build_folders():
    """清理构建文件夹"""
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"清理文件夹: {folder}")
            shutil.rmtree(folder)

def build_exe():
    """使用PyInstaller构建exe文件"""
    print("开始构建exe文件...")
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--name=WatermarkApp',
        '--windowed',  # 使用GUI模式，不显示控制台
        '--icon=resources/icon.ico',  # 如果有图标文件
        '--add-data=resources;resources',  # 添加资源文件
        '--add-data=templates;templates',  # 添加模板文件
        'main.py'
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists('resources/icon.ico'):
        cmd.remove('--icon=resources/icon.ico')
    
    # 执行构建命令
    try:
        subprocess.run(cmd, check=True)
        print("构建成功！exe文件位于 dist/WatermarkApp 文件夹中")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def create_release_package():
    """创建发布包"""
    if not os.path.exists('dist/WatermarkApp'):
        print("构建文件夹不存在，请先构建应用程序")
        return False
    
    # 创建发布文件夹
    release_folder = 'release'
    if not os.path.exists(release_folder):
        os.makedirs(release_folder)
    
    # 创建zip文件
    release_file = os.path.join(release_folder, 'WatermarkApp_release.zip')
    print(f"创建发布包: {release_file}")
    
    shutil.make_archive(
        os.path.splitext(release_file)[0],  # 不带扩展名的路径
        'zip',  # 压缩格式
        'dist',  # 源目录
        'WatermarkApp'  # 要压缩的文件夹
    )
    
    print(f"发布包创建成功: {release_file}")
    return True

if __name__ == "__main__":
    # 清理旧的构建文件
    clean_build_folders()
    
    # 构建exe
    if build_exe():
        # 创建发布包
        create_release_package()
        print("打包过程完成！")
    else:
        print("打包过程失败！")
        sys.exit(1)