#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

class ConfigManager:
    """配置管理类，负责水印模板的保存和加载"""
    
    def __init__(self):
        # 创建模板目录
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
        os.makedirs(self.template_dir, exist_ok=True)
        
        # 默认配置
        self.default_config = {
            'text': '水印文本',
            'font_size': 24,
            'color': (255, 0, 0, 128),  # 半透明红色
            'opacity': 50,
            'position': 4  # 中心位置
        }
        
        # 上次使用的配置文件路径
        self.last_config_path = os.path.join(self.template_dir, "last_config.json")
    
    def save_template(self, template_name, config):
        """保存水印模板"""
        template_path = os.path.join(self.template_dir, f"{template_name}.json")
        
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        # 同时保存为上次使用的配置
        self.save_last_config(config)
        
        return True
    
    def load_template(self, template_name):
        """加载水印模板"""
        if template_name == "默认模板":
            return self.default_config
        
        template_path = os.path.join(self.template_dir, f"{template_name}.json")
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def delete_template(self, template_name):
        """删除水印模板"""
        if template_name == "默认模板":
            return False
        
        template_path = os.path.join(self.template_dir, f"{template_name}.json")
        
        if os.path.exists(template_path):
            try:
                os.remove(template_path)
                return True
            except:
                return False
        
        return False
    
    def get_all_templates(self):
        """获取所有模板名称"""
        templates = ["默认模板"]
        
        if os.path.exists(self.template_dir):
            for file in os.listdir(self.template_dir):
                if file.endswith(".json") and file != "last_config.json":
                    templates.append(os.path.splitext(file)[0])
        
        return templates
    
    def save_last_config(self, config):
        """保存上次使用的配置"""
        with open(self.last_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def load_default_config(self):
        """加载默认配置或上次使用的配置"""
        if os.path.exists(self.last_config_path):
            try:
                with open(self.last_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config
        
        return self.default_config