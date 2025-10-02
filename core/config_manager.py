import os
import json
from typing import Dict, Any, Optional, List

class ConfigManager:
    """配置管理模块，负责水印模板的保存、加载和管理"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.current_config: Dict[str, Any] = self._get_default_config()
        
        # 确保模板目录存在
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
    
    def save_template(self, name: str) -> bool:
        """
        保存当前配置为模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 保存是否成功
        """
        if not name:
            return False
            
        # 构建文件路径
        file_path = os.path.join(self.templates_dir, f"{name}.json")
        
        try:
            # 保存配置到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存模板时出错: {str(e)}")
            return False
    
    def load_template(self, name: str) -> bool:
        """
        加载模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 加载是否成功
        """
        # 构建文件路径
        file_path = os.path.join(self.templates_dir, f"{name}.json")
        
        if not os.path.exists(file_path):
            print(f"模板不存在: {name}")
            return False
            
        try:
            # 从文件加载配置
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 更新当前配置
            self.current_config = config
            return True
        except Exception as e:
            print(f"加载模板时出错: {str(e)}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """
        删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 删除是否成功
        """
        # 构建文件路径
        file_path = os.path.join(self.templates_dir, f"{name}.json")
        
        if not os.path.exists(file_path):
            print(f"模板不存在: {name}")
            return False
            
        try:
            # 删除文件
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"删除模板时出错: {str(e)}")
            return False
    
    def get_template_list(self) -> List[str]:
        """
        获取所有模板名称列表
        
        Returns:
            List[str]: 模板名称列表
        """
        templates = []
        
        # 遍历模板目录
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.endswith('.json'):
                    # 去除扩展名
                    template_name = os.path.splitext(file)[0]
                    templates.append(template_name)
                    
        return templates
    
    def set_current_config(self, config: Dict[str, Any]) -> None:
        """
        设置当前配置
        
        Args:
            config: 配置字典
        """
        self.current_config = config
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            Dict[str, Any]: 当前配置
        """
        return self.current_config
    
    def save_last_config(self) -> bool:
        """
        保存最后一次使用的配置
        
        Returns:
            bool: 保存是否成功
        """
        return self.save_template("_last_config")
    
    def load_last_config(self) -> bool:
        """
        加载最后一次使用的配置
        
        Returns:
            bool: 加载是否成功
        """
        # 尝试加载最后一次配置
        if not self.load_template("_last_config"):
            # 如果失败，加载默认配置
            self.current_config = self._get_default_config()
            return False
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置
        """
        return {
            "watermark": {
                "text": "水印示例",
                "font_name": "Arial",
                "font_size": 36,
                "font_color": [255, 255, 255],
                "opacity": 50,
                "position": "center",
                "custom_position": None
            },
            "export": {
                "format": "JPEG",
                "naming_rule": {
                    "type": "original",
                    "prefix": "",
                    "suffix": ""
                }
            }
        }