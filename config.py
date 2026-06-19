"""
配置管理模块
负责读取、保存和管理应用程序配置
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 如果配置文件不存在，创建默认配置
                self._create_default_config()
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            self._create_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """创建默认配置"""
        self.config = {
            "ai_service": {
                "provider": "openai_compatible",
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            "hotkey": {
                "trigger": "ctrl+shift+q",
                "enabled": True
            },
            "clipboard": {
                "wait_mode_timeout": 15,
                "check_interval": 0.2,
                "ignore_patterns": [
                    "[Violation]",
                    "Permissions policy",
                    "Failed to load resource"
                ]
            },
            "ui": {
                "theme": "dark",
                "appearance_mode": "dark",
                "color_theme": "blue",
                "window_width": 580,
                "window_height": 500,
                "auto_close_seconds": 0,
                "font_size": 14
            },
            "general": {
                "auto_start": False,
                "minimize_to_tray": True,
                "show_notifications": True,
                "language": "auto",
                "enable_logging": False
            }
        }
        self.save()
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号分隔的路径）
        
        Args:
            key_path: 配置键路径，如 "ai_service.api_key"
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置值（支持点号分隔的路径）
        
        Args:
            key_path: 配置键路径，如 "ai_service.api_key"
            value: 要设置的值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 遍历到倒数第二层
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置最后一层的值
        config[keys[-1]] = value
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI服务配置"""
        return self.get("ai_service", {})
    
    def set_ai_config(self, **kwargs) -> None:
        """
        设置AI服务配置
        
        Args:
            **kwargs: AI配置参数
        """
        for key, value in kwargs.items():
            self.set(f"ai_service.{key}", value)
    
    def get_hotkey(self) -> str:
        """获取热键配置"""
        return self.get("hotkey.trigger", "ctrl+shift+a")
    
    def set_hotkey(self, hotkey: str) -> None:
        """设置热键"""
        self.set("hotkey.trigger", hotkey)
    
    def get_prompt(self, prompt_type: str = "optimize") -> str:
        """
        获取提示词
        
        Args:
            prompt_type: 提示词类型 (optimize, explain, fix, translate, summarize)
        
        Returns:
            提示词内容
        """
        return self.get(f"prompts.{prompt_type}", "")
    
    def set_prompt(self, prompt_type: str, content: str) -> None:
        """
        设置提示词
        
        Args:
            prompt_type: 提示词类型
            content: 提示词内容
        """
        self.set(f"prompts.{prompt_type}", content)
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.get("ui", {})
    
    def is_api_configured(self) -> bool:
        """检查API是否已配置"""
        api_key = self.get("ai_service.api_key", "")
        base_url = self.get("ai_service.base_url", "")
        return bool(api_key and base_url)
    
    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self._create_default_config()
    
    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return json.dumps(self.config, indent=2, ensure_ascii=False)


# 全局配置实例
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config() -> Config:
    """重新加载配置"""
    global _config_instance
    _config_instance = Config()
    return _config_instance
