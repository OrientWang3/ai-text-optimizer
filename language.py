"""
多语言支持模块
"""

import json
import locale
import ctypes
from pathlib import Path
from typing import Dict, Optional


def get_system_language() -> str:
    """
    获取系统语言

    Returns:
        "zh" for Chinese, "en" for others
    """
    try:
        # 方法1: 使用Windows API获取系统语言
        windll = ctypes.windll.kernel32
        lang_id = windll.GetUserDefaultUILanguage()

        # 中文语言ID: 0x0804(简体), 0x0404(繁体), 0x0C04(香港), 0x1404(澳门)
        chinese_langs = [0x0804, 0x0404, 0x0C04, 0x1404, 0x1004, 0x0409]

        if lang_id in chinese_langs:
            return "zh"

        # 方法2: 使用locale模块
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang and sys_lang.startswith("zh"):
            return "zh"

        return "en"

    except Exception:
        # 默认中文
        return "zh"

# 语言包
LANGUAGE_PACKS = {
    "zh": {
        # 通用
        "app_name": "AI文本优化器",
        "ok": "确定",
        "cancel": "取消",
        "save": "保存",
        "close": "关闭",
        "delete": "删除",
        "edit": "编辑",
        "add": "添加",
        "reset": "重置",
        "test": "测试",
        "on": "开启",
        "off": "关闭",

        # 托盘菜单
        "tray_hotkey": "热键",
        "tray_templates": "提示词模板",
        "tray_settings": "设置",
        "tray_quit": "退出",
        "tray_hotkey_on": "热键: 开启",
        "tray_hotkey_off": "热键: 关闭",

        # 浮动窗口
        "window_title": "AI文本优化器",
        "original": "原文",
        "ai_result": "AI分析结果",
        "copy_result": "复制结果",
        "copy_original": "复制原文",
        "copied": "已复制!",
        "original_copied": "原文已复制!",
        "analyzing": "正在分析...",

        # 热键设置
        "hotkey_title": "设置热键",
        "hotkey_current": "当前热键",
        "hotkey_new": "新热键",
        "hotkey_modifiers": "修饰键",
        "hotkey_key": "按键",
        "hotkey_preset": "预设",

        # 模板窗口
        "template_title": "提示词模板",
        "template_list": "模板列表",
        "template_preview": "预览",
        "template_use": "使用模板",
        "template_add": "添加模板",
        "template_edit": "编辑模板",
        "template_name": "名称",
        "template_desc": "描述",
        "template_category": "分类",
        "template_prompt": "提示词内容",
        "template_key": "标识",
        "template_selected": "已选择",

        # 设置窗口
        "settings_title": "设置",
        "settings_ai": "AI服务配置",
        "settings_preset": "预设服务",
        "settings_custom": "自定义",
        "settings_api_key": "API密钥",
        "settings_base_url": "API地址",
        "settings_model": "模型名称",
        "settings_format": "API格式",
        "settings_test": "测试连接",
        "settings_hotkey": "热键配置",
        "settings_prompt": "自定义提示词",
        "settings_prompt_desc": "内置智能提示词会自动检测内容类型，可添加额外指令：",
        "settings_ui": "界面配置",
        "settings_theme": "主题",
        "settings_language": "语言",
        "settings_saved": "设置已保存!",
        "settings_save_failed": "保存失败!",
        "settings_testing": "正在测试...",
        "settings_connected": "连接成功!",
        "settings_connect_failed": "连接失败",

        # 提示信息
        "no_text": "没有文本",
        "no_text_msg": "剪贴板为空!\n\n使用方法:\n1. 选中文本\n2. 按 Ctrl+C 复制\n3. 按热键",
        "timeout": "超时",
        "timeout_msg": "未检测到文本复制\n\n请重试",
        "wait_mode": "等待模式",
        "wait_mode_msg": "请选中文本，然后按 Ctrl+C",
        "ai_error": "AI错误",
        "error": "错误",

        # 启动信息
        "start_title": "AI文本优化器",
        "start_hotkey": "热键",
        "start_template": "当前模板",
        "start_usage": "使用方法",
        "start_step1": "1. 在任意软件中选中文本",
        "start_step2": "2. 按 Ctrl+C 复制",
        "start_step3": "3. 按热键触发",
        "start_step4": "4. 查看AI分析结果",
        "start_change": "更改设置",
        "start_change_tip": "右键托盘图标进行设置",
        "start_ready": "就绪",

        # 模板分类
        "cat_code": "代码",
        "cat_debug": "调试",
        "cat_config": "配置",
        "cat_log": "日志",
        "cat_general": "通用",
        "cat_custom": "自定义",

        # 预设模板名称
        "tpl_code_fix": "[Bug] 代码修复",
        "tpl_code_fix_desc": "分析错误并提供修复方案",
        "tpl_code_optimize": "[Code] 代码优化",
        "tpl_code_optimize_desc": "优化代码性能和可读性",
        "tpl_code_explain": "[Code] 代码解释",
        "tpl_code_explain_desc": "解释代码功能",
        "tpl_code_review": "[Code] 代码审查",
        "tpl_code_review_desc": "代码审查并提供建议",
        "tpl_bug_debug": "[Bug] 调试追踪",
        "tpl_bug_debug_desc": "调试并追踪问题",
        "tpl_bug_stack": "[Bug] 堆栈分析",
        "tpl_bug_stack_desc": "分析堆栈跟踪信息",
        "tpl_config_fix": "[Config] 配置修复",
        "tpl_config_fix_desc": "修复配置问题",
        "tpl_log_analyze": "[Log] 日志分析",
        "tpl_log_analyze_desc": "分析日志并定位问题",
        "tpl_translate": "[General] 翻译",
        "tpl_translate_desc": "翻译文本",
        "tpl_summarize": "[General] 总结",
        "tpl_summarize_desc": "总结内容要点",

        # 热键设置
        "hotkey_press": "按下新的热键组合",
        "hotkey_example": "例如: Ctrl+Shift+Q, Alt+F1, Ctrl+Alt+X",
        "hotkey_waiting": "请按下热键...",
        "hotkey_saved": "热键已更新！",
        "hotkey_cancelled": "已取消",
        "hotkey_start_listen": "开始监听",
        "hotkey_stop_listen": "停止监听 (ESC取消)",
        "hotkey_press_esc": "按下ESC取消",
    },

    "en": {
        # General
        "app_name": "AI Text Optimizer",
        "ok": "OK",
        "cancel": "Cancel",
        "save": "Save",
        "close": "Close",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "reset": "Reset",
        "test": "Test",
        "on": "ON",
        "off": "OFF",

        # Tray menu
        "tray_hotkey": "Hotkey",
        "tray_templates": "Templates",
        "tray_settings": "Settings",
        "tray_quit": "Quit",
        "tray_hotkey_on": "Hotkey: ON",
        "tray_hotkey_off": "Hotkey: OFF",

        # Floating window
        "window_title": "AI Text Optimizer",
        "original": "Original",
        "ai_result": "AI Result",
        "copy_result": "Copy Result",
        "copy_original": "Copy Original",
        "copied": "Copied!",
        "original_copied": "Original copied!",
        "analyzing": "Analyzing...",

        # Hotkey settings
        "hotkey_title": "Set Hotkey",
        "hotkey_current": "Current Hotkey",
        "hotkey_new": "New Hotkey",
        "hotkey_modifiers": "Modifiers",
        "hotkey_key": "Key",
        "hotkey_preset": "Presets",

        # Template window
        "template_title": "Prompt Templates",
        "template_list": "Templates",
        "template_preview": "Preview",
        "template_use": "Use Template",
        "template_add": "Add Template",
        "template_edit": "Edit Template",
        "template_name": "Name",
        "template_desc": "Description",
        "template_category": "Category",
        "template_prompt": "Prompt Content",
        "template_key": "Key",
        "template_selected": "Selected",

        # Settings window
        "settings_title": "Settings",
        "settings_ai": "AI Service",
        "settings_preset": "Preset",
        "settings_custom": "Custom",
        "settings_api_key": "API Key",
        "settings_base_url": "Base URL",
        "settings_model": "Model",
        "settings_format": "API Format",
        "settings_test": "Test Connection",
        "settings_hotkey": "Hotkey",
        "settings_prompt": "Custom Prompt",
        "settings_prompt_desc": "Built-in smart prompts auto-detect content type. Add extra instructions:",
        "settings_ui": "UI Settings",
        "settings_theme": "Theme",
        "settings_language": "Language",
        "settings_saved": "Settings saved!",
        "settings_save_failed": "Save failed!",
        "settings_testing": "Testing...",
        "settings_connected": "Connected!",
        "settings_connect_failed": "Connection failed",

        # Messages
        "no_text": "No Text",
        "no_text_msg": "Clipboard is empty!\n\nHow to use:\n1. Select text\n2. Press Ctrl+C\n3. Press hotkey",
        "timeout": "Timeout",
        "timeout_msg": "No text copied\n\nPlease try again",
        "wait_mode": "Wait Mode",
        "wait_mode_msg": "Select text, then press Ctrl+C",
        "ai_error": "AI Error",
        "error": "Error",

        # Start info
        "start_title": "AI Text Optimizer",
        "start_hotkey": "Hotkey",
        "start_template": "Template",
        "start_usage": "Usage",
        "start_step1": "1. Select text in any software",
        "start_step2": "2. Press Ctrl+C to copy",
        "start_step3": "3. Press hotkey to trigger",
        "start_step4": "4. View AI result",
        "start_change": "Settings",
        "start_change_tip": "Right-click tray icon for settings",
        "start_ready": "Ready",

        # Template categories
        "cat_code": "Code",
        "cat_debug": "Debug",
        "cat_config": "Config",
        "cat_log": "Log",
        "cat_general": "General",
        "cat_custom": "Custom",

        # Preset template names
        "tpl_code_fix": "[Bug] Code Fix",
        "tpl_code_fix_desc": "Analyze error and provide fix",
        "tpl_code_optimize": "[Code] Optimize",
        "tpl_code_optimize_desc": "Optimize code performance",
        "tpl_code_explain": "[Code] Explain",
        "tpl_code_explain_desc": "Explain what code does",
        "tpl_code_review": "[Code] Review",
        "tpl_code_review_desc": "Code review with suggestions",
        "tpl_bug_debug": "[Bug] Debug",
        "tpl_bug_debug_desc": "Debug and trace issues",
        "tpl_bug_stack": "[Bug] Stack Trace",
        "tpl_bug_stack_desc": "Analyze stack traces",
        "tpl_config_fix": "[Config] Fix",
        "tpl_config_fix_desc": "Fix configuration issues",
        "tpl_log_analyze": "[Log] Analyze",
        "tpl_log_analyze_desc": "Analyze logs and find issues",
        "tpl_translate": "[General] Translate",
        "tpl_translate_desc": "Translate text",
        "tpl_summarize": "[General] Summarize",
        "tpl_summarize_desc": "Summarize content",

        # Hotkey settings
        "hotkey_press": "Press new hotkey combination",
        "hotkey_example": "Example: Ctrl+Shift+Q, Alt+F1, Ctrl+Alt+X",
        "hotkey_waiting": "Press hotkey...",
        "hotkey_saved": "Hotkey updated!",
        "hotkey_cancelled": "Cancelled",
        "hotkey_start_listen": "Start Listening",
        "hotkey_stop_listen": "Stop (ESC to cancel)",
        "hotkey_press_esc": "Press ESC to cancel",
    }
}


class LanguageManager:
    """语言管理器"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._current_lang = "zh"
        self._load_language()

    def _load_language(self):
        """从配置加载语言"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang = config.get("general", {}).get("language", "zh")
                    # "auto" 或无效值默认使用中文
                    if lang == "auto" or lang not in LANGUAGE_PACKS:
                        lang = "zh"
                    self._current_lang = lang
        except:
            self._current_lang = "zh"

    def get_lang(self) -> str:
        """获取当前语言"""
        return self._current_lang

    def set_lang(self, lang: str):
        """设置语言"""
        if lang in LANGUAGE_PACKS:
            self._current_lang = lang

    def t(self, key: str) -> str:
        """
        翻译

        Args:
            key: 翻译键

        Returns:
            翻译后的文本
        """
        pack = LANGUAGE_PACKS.get(self._current_lang, LANGUAGE_PACKS["zh"])
        return pack.get(key, key)

    def get_lang_name(self, lang_code: str) -> str:
        """获取语言显示名称"""
        names = {
            "zh": "中文",
            "en": "English"
        }
        return names.get(lang_code, lang_code)

    def get_available_langs(self) -> list:
        """获取可用语言列表"""
        return list(LANGUAGE_PACKS.keys())


# 全局实例
_lang_manager: Optional[LanguageManager] = None


def get_lang_manager() -> LanguageManager:
    """获取全局语言管理器"""
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager


def t(key: str) -> str:
    """快捷翻译函数"""
    return get_lang_manager().t(key)
