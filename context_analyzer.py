"""
上下文分析器
自动检测当前软件和分析文本类型
"""

import re
import subprocess
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WindowContext:
    """窗口上下文信息"""
    app_name: str           # 应用名称 (VSCode, Chrome, Terminal, etc.)
    window_title: str       # 窗口标题
    process_name: str       # 进程名
    category: str           # 分类 (editor, browser, terminal, other)


@dataclass
class TextAnalysis:
    """文本分析结果"""
    content_type: str       # 内容类型 (error, code, log, config, plain)
    language: str           # 编程语言 (python, javascript, etc.)
    confidence: float       # 置信度 (0-1)
    keywords: list          # 关键词
    description: str        # 描述


class ContextAnalyzer:
    """上下文分析器"""

    # 已知应用映射
    KNOWN_APPS = {
        # 编辑器
        "code": ("VS Code", "editor"),
        "code.exe": ("VS Code", "editor"),
        "sublime_text": ("Sublime Text", "editor"),
        "notepad++": ("Notepad++", "editor"),
        "idea64": ("IntelliJ IDEA", "editor"),
        "idea": ("IntelliJ IDEA", "editor"),
        "pycharm64": ("PyCharm", "editor"),
        "webstorm64": ("WebStorm", "editor"),
        "notepad": ("记事本", "editor"),
        "word": ("Word", "editor"),
        "WINWORD": ("Word", "editor"),

        # 浏览器
        "chrome": ("Chrome", "browser"),
        "chrome.exe": ("Chrome", "browser"),
        "firefox": ("Firefox", "browser"),
        "msedge": ("Edge", "browser"),
        "edge": ("Edge", "browser"),
        "brave": ("Brave", "browser"),
        "opera": ("Opera", "browser"),

        # 终端
        "cmd": ("命令提示符", "terminal"),
        "cmd.exe": ("命令提示符", "terminal"),
        "powershell": ("PowerShell", "terminal"),
        "pwsh": ("PowerShell", "terminal"),
        "windowsterminal": ("Windows Terminal", "terminal"),
        "wt": ("Windows Terminal", "terminal"),
        "hyper": ("Hyper", "terminal"),
        "git-bash": ("Git Bash", "terminal"),

        # 通讯/其他
        "slack": ("Slack", "messaging"),
        "discord": ("Discord", "messaging"),
        "telegram": ("Telegram", "messaging"),
        "wechat": ("微信", "messaging"),
        "WeChat": ("微信", "messaging"),
    }

    # 错误关键词
    ERROR_KEYWORDS = [
        "error", "exception", "traceback", "fatal", "failed", "failure",
        "错误", "异常", "失败", "崩溃",
        "Error:", "Exception:", "Traceback",
        "errno", "err:", "warn:", "warning",
        "undefined", "null", "None", "NaN",
        "cannot", "unable", "invalid",
        "TypeError", "ValueError", "KeyError", "IndexError",
        "SyntaxError", "ImportError", "AttributeError",
        "ReferenceError", "RangeError", "SyntaxError",
        "FATAL", "CRITICAL", "panic",
        "stack trace", "at line", "at position",
        "errno", "EACCES", "ENOENT", "EPERM",
    ]

    # 代码关键词
    CODE_KEYWORDS = [
        "function", "class", "def", "import", "from", "return",
        "if", "else", "for", "while", "try", "catch",
        "const", "let", "var", "async", "await",
        "public", "private", "protected", "static",
        "void", "int", "string", "bool", "float",
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE",
        "console.log", "print", "echo", "printf",
        "#include", "using namespace", "package",
        "interface", "enum", "struct", "type",
    ]

    # 日志关键词
    LOG_KEYWORDS = [
        "log", "debug", "info", "warn", "error", "fatal",
        "timestamp", "datetime", "level",
        "[DEBUG]", "[INFO]", "[WARN]", "[ERROR]",
        "2024-", "2023-", "2025-", "2026-",
        "T00:", "T12:", "T23:",
    ]

    # 配置关键词
    CONFIG_KEYWORDS = [
        "config", "setting", "env", "environment",
        "json", "yaml", "yml", "toml", "ini", "xml",
        "key", "value", "port", "host", "url",
        "database", "redis", "mysql", "postgres",
        "api_key", "secret", "token", "password",
    ]

    def __init__(self):
        """初始化分析器"""
        pass

    def get_active_window(self) -> WindowContext:
        """
        获取当前活动窗口信息

        Returns:
            WindowContext: 窗口上下文信息
        """
        try:
            # 使用Windows API获取活动窗口
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            # 获取前台窗口句柄
            hwnd = user32.GetForegroundWindow()

            # 获取窗口标题
            length = user32.GetWindowTextLengthW(hwnd)
            title_buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, title_buffer, length + 1)
            window_title = title_buffer.value

            # 获取进程ID
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            # 获取进程名
            process_name = self._get_process_name(pid.value)

            # 识别应用
            app_name, category = self._identify_app(process_name, window_title)

            return WindowContext(
                app_name=app_name,
                window_title=window_title,
                process_name=process_name,
                category=category
            )

        except Exception as e:
            print(f"获取活动窗口失败: {e}")
            return WindowContext(
                app_name="未知应用",
                window_title="",
                process_name="unknown",
                category="other"
            )

    def _get_process_name(self, pid: int) -> str:
        """
        根据PID获取进程名

        Args:
            pid: 进程ID

        Returns:
            进程名
        """
        try:
            import ctypes
            from ctypes import wintypes

            # 打开进程
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010

            kernel32 = ctypes.windll.kernel32
            process_handle = kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                False,
                pid
            )

            if process_handle:
                # 获取进程名
                buffer = ctypes.create_unicode_buffer(512)
                psapi = ctypes.windll.psapi
                psapi.GetModuleBaseNameW(process_handle, None, buffer, 512)

                kernel32.CloseHandle(process_handle)
                return buffer.value.lower()

        except Exception:
            pass

        return "unknown"

    def _identify_app(self, process_name: str, window_title: str) -> Tuple[str, str]:
        """
        识别应用

        Args:
            process_name: 进程名
            window_title: 窗口标题

        Returns:
            (应用名称, 分类)
        """
        # 移除.exe后缀
        clean_name = process_name.replace(".exe", "")

        # 查找已知应用
        for key, (name, category) in self.KNOWN_APPS.items():
            if key.lower() in clean_name or key.lower() in window_title.lower():
                return name, category

        # 根据窗口标题推断
        title_lower = window_title.lower()
        if any(x in title_lower for x in ["visual studio code", "vscode"]):
            return "VS Code", "editor"
        elif any(x in title_lower for x in ["chrome", "google"]):
            return "Chrome", "browser"
        elif any(x in title_lower for x in ["firefox", "mozilla"]):
            return "Firefox", "browser"
        elif any(x in title_lower for x in ["terminal", "powershell", "cmd"]):
            return "终端", "terminal"
        elif any(x in title_lower for x in ["claude", "anthropic"]):
            return "Claude", "ai"

        return process_name or "未知应用", "other"

    def analyze_text(self, text: str, context: WindowContext) -> TextAnalysis:
        """
        分析文本内容

        Args:
            text: 要分析的文本
            context: 窗口上下文

        Returns:
            TextAnalysis: 分析结果
        """
        text_lower = text.lower()
        lines = text.strip().split('\n')

        # 计算各种类型的得分
        error_score = self._calculate_error_score(text, text_lower)
        code_score = self._calculate_code_score(text, text_lower, context)
        log_score = self._calculate_log_score(text, text_lower)
        config_score = self._calculate_config_score(text, text_lower)

        # 确定主要类型
        scores = {
            "error": error_score,
            "code": code_score,
            "log": log_score,
            "config": config_score,
        }

        # 如果来自终端，增加错误和日志的权重
        if context.category == "terminal":
            scores["error"] *= 1.5
            scores["log"] *= 1.3

        # 如果来自编辑器，增加代码的权重
        if context.category == "editor":
            scores["code"] *= 1.5

        # 找出最高分的类型
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]

        # 如果所有分数都很低，认为是普通文本
        if max_score < 0.3:
            content_type = "plain"
            confidence = 0.8
        else:
            content_type = max_type
            confidence = min(max_score, 1.0)

        # 检测编程语言
        language = self._detect_language(text, text_lower, context)

        # 提取关键词
        keywords = self._extract_keywords(text, content_type)

        # 生成描述
        description = self._generate_description(content_type, language, context)

        return TextAnalysis(
            content_type=content_type,
            language=language,
            confidence=confidence,
            keywords=keywords,
            description=description
        )

    def _calculate_error_score(self, text: str, text_lower: str) -> float:
        """计算错误得分"""
        score = 0.0
        matched = 0

        for keyword in self.ERROR_KEYWORDS:
            if keyword.lower() in text_lower:
                matched += 1
                # 某些关键词权重更高
                if keyword in ["Traceback", "Exception", "Error:", "FATAL"]:
                    score += 0.3
                else:
                    score += 0.1

        # 检查是否有行号信息
        if re.search(r'line \d+|at \w+\.\w+:\d+', text_lower):
            score += 0.2

        # 检查是否有堆栈跟踪格式
        if re.search(r'at .+\(.+:\d+:\d+\)', text):
            score += 0.3

        return min(score, 1.0)

    def _calculate_code_score(self, text: str, text_lower: str, context: WindowContext) -> float:
        """计算代码得分"""
        score = 0.0

        # 检查代码关键词
        for keyword in self.CODE_KEYWORDS:
            if keyword.lower() in text_lower:
                score += 0.1

        # 检查代码结构
        if re.search(r'\{[\s\S]*\}', text):  # 花括号
            score += 0.2
        if re.search(r'\([\s\S]*\)', text):  # 圆括号
            score += 0.1
        if re.search(r'function\s+\w+|def\s+\w+|class\s+\w+', text):  # 函数/类定义
            score += 0.3
        if re.search(r'import\s+\w+|from\s+\w+\s+import', text):  # 导入语句
            score += 0.2

        # 检查缩进结构
        lines = text.strip().split('\n')
        indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
        if indented_lines > len(lines) * 0.3:
            score += 0.2

        # 如果来自编辑器，额外加分
        if context.category == "editor":
            score *= 1.2

        return min(score, 1.0)

    def _calculate_log_score(self, text: str, text_lower: str) -> float:
        """计算日志得分"""
        score = 0.0

        # 检查日志关键词
        for keyword in self.LOG_KEYWORDS:
            if keyword.lower() in text_lower:
                score += 0.1

        # 检查时间戳格式
        if re.search(r'\d{4}-\d{2}-\d{2}', text):
            score += 0.3
        if re.search(r'\d{2}:\d{2}:\d{2}', text):
            score += 0.2

        # 检查日志级别标记
        if re.search(r'\[(DEBUG|INFO|WARN|ERROR|FATAL)\]', text):
            score += 0.3

        return min(score, 1.0)

    def _calculate_config_score(self, text: str, text_lower: str) -> float:
        """计算配置得分"""
        score = 0.0

        # 检查配置关键词
        for keyword in self.CONFIG_KEYWORDS:
            if keyword.lower() in text_lower:
                score += 0.1

        # 检查配置格式
        if re.search(r'^\s*\w+\s*[:=]\s*.+', text, re.MULTILINE):  # key: value 或 key=value
            score += 0.3
        if re.search(r'[\{\}]', text):  # JSON格式
            score += 0.2
        if re.search(r'---\n', text):  # YAML格式
            score += 0.2

        return min(score, 1.0)

    def _detect_language(self, text: str, text_lower: str, context: WindowContext) -> str:
        """
        检测编程语言

        Args:
            text: 原始文本
            text_lower: 小写文本
            context: 窗口上下文

        Returns:
            编程语言名称
        """
        # Python
        if any(x in text for x in ['def ', 'import ', 'from ', 'print(', '__init__', 'self.']):
            return "python"

        # JavaScript/TypeScript
        if any(x in text for x in ['const ', 'let ', 'var ', 'function(', '=>', 'console.log', 'async ', 'await ']):
            if 'interface ' in text or 'type ' in text or ': string' in text:
                return "typescript"
            return "javascript"

        # Java
        if any(x in text for x in ['public class', 'private ', 'protected ', 'System.out', 'void main']):
            return "java"

        # C/C++
        if any(x in text for x in ['#include', 'int main', 'printf(', 'cout <<', 'using namespace']):
            return "c/c++"

        # Go
        if any(x in text for x in ['func ', 'package ', 'import (', 'fmt.Print']):
            return "go"

        # Rust
        if any(x in text for x in ['fn ', 'let mut', 'println!', 'impl ', 'pub struct']):
            return "rust"

        # SQL
        if any(x in text_lower for x in ['select ', 'insert ', 'update ', 'delete ', 'create table']):
            return "sql"

        # Shell/Bash
        if any(x in text for x in ['#!/bin/bash', 'echo ', 'export ', '$(', 'sudo ']):
            return "bash"

        # HTML
        if any(x in text_lower for x in ['<html', '<div', '<span', '<!doctype']):
            return "html"

        # CSS
        if re.search(r'[\w-]+\s*\{[^}]*\}', text):
            return "css"

        # JSON
        if re.search(r'^\s*[\{\[]', text) and re.search(r'[\}\]]\s*$', text):
            return "json"

        # YAML
        if re.search(r'^\w+:', text, re.MULTILINE):
            return "yaml"

        return "unknown"

    def _extract_keywords(self, text: str, content_type: str) -> list:
        """
        提取关键词

        Args:
            text: 文本
            content_type: 内容类型

        Returns:
            关键词列表
        """
        keywords = []

        if content_type == "error":
            # 提取错误类型
            error_patterns = [
                r'(\w+Error)',
                r'(\w+Exception)',
                r'Error:\s*(.+)',
                r'Exception:\s*(.+)',
            ]
            for pattern in error_patterns:
                matches = re.findall(pattern, text)
                keywords.extend(matches[:3])

        elif content_type == "code":
            # 提取函数名和类名
            func_patterns = [
                r'function\s+(\w+)',
                r'def\s+(\w+)',
                r'class\s+(\w+)',
                r'const\s+(\w+)',
            ]
            for pattern in func_patterns:
                matches = re.findall(pattern, text)
                keywords.extend(matches[:3])

        return keywords[:5]  # 最多返回5个关键词

    def _generate_description(self, content_type: str, language: str, context: WindowContext) -> str:
        """
        生成描述

        Args:
            content_type: 内容类型
            language: 编程语言
            context: 窗口上下文

        Returns:
            描述文本
        """
        type_desc = {
            "error": "错误信息",
            "code": "代码片段",
            "log": "日志输出",
            "config": "配置内容",
            "plain": "普通文本",
        }

        parts = []

        # 来源
        if context.app_name != "未知应用":
            parts.append(f"来自 {context.app_name}")

        # 内容类型
        parts.append(type_desc.get(content_type, "未知类型"))

        # 编程语言
        if language != "unknown":
            parts.append(f"({language})")

        return " | ".join(parts) if parts else "未知内容"

    def generate_smart_prompt(self, text: str, analysis: TextAnalysis, context: WindowContext) -> str:
        """
        生成智能提示词 - 专注于代码修改/优化
        要求AI返回纯文本格式，不使用Markdown
        """
        base_prompts = {
            "error": """你是一个专业的代码调试专家。请分析以下错误并提供修复方案。

重要：请用纯文本格式回答，不要使用Markdown语法（不要用**加粗**、不要用```代码块```、不要用#标题）。
代码直接写出来即可，用缩进表示层级。

来源: {source}
语言: {language}
错误信息:
{text}

请直接提供：
1. 错误原因：一句话说明为什么会报错
2. 修复代码：直接给出修改后的代码
3. 修改说明：简要说明改了哪里

回答要简洁直接，重点是代码修复。""",

            "code": """你是一个代码优化专家。请分析以下代码并提供优化版本。

重要：请用纯文本格式回答，不要使用Markdown语法（不要用**加粗**、不要用```代码块```、不要用#标题）。
代码直接写出来即可，用缩进表示层级。

来源: {source}
语言: {language}
原始代码:
{text}

请直接提供：
1. 优化后的代码：直接给出改进后的完整代码
2. 改进点：列出主要的优化内容
3. 注意事项：使用新代码时需要注意什么

回答要简洁，重点是提供可直接使用的优化代码。""",

            "log": """你是一个问题排查专家。请分析以下日志并提供解决方案。

重要：请用纯文本格式回答，不要使用Markdown语法（不要用**加粗**、不要用```代码块```、不要用#标题）。
代码直接写出来即可，用缩进表示层级。

来源: {source}
日志内容:
{text}

请直接提供：
1. 问题定位：从日志中看出什么问题
2. 解决步骤：按优先级列出排查和解决步骤
3. 相关代码：如果需要修改代码，直接给出修改方案

回答要简洁实用。""",

            "config": """你是一个配置专家。请分析并优化以下配置。

重要：请用纯文本格式回答，不要使用Markdown语法（不要用**加粗**、不要用```代码块```、不要用#标题）。
代码直接写出来即可，用缩进表示层级。

来源: {source}
配置内容:
{text}

请直接提供：
1. 优化后的配置：直接给出改进后的配置
2. 修改说明：改了哪些项，为什么改
3. 注意事项：使用新配置需要注意什么

回答要简洁，重点是提供可直接使用的配置。""",

            "plain": """请分析以下内容并提供优化建议。

重要：请用纯文本格式回答，不要使用Markdown语法（不要用**加粗**、不要用```代码块```、不要用#标题）。
代码直接写出来即可，用缩进表示层级。

来源: {source}
内容:
{text}

请根据内容类型提供：
1. 内容分析：这段内容是什么/做了什么
2. 优化建议：如何改进（如果是代码则提供优化代码）
3. 补充说明：相关的最佳实践

回答要简洁实用。""",
        }

        # 获取对应的提示词模板
        prompt_template = base_prompts.get(analysis.content_type, base_prompts["plain"])

        # 填充模板
        prompt = prompt_template.format(
            source=f"{context.app_name} ({context.category})",
            language=analysis.language if analysis.language != "unknown" else "",
            text=text[:3000]
        )

        return prompt


# 全局实例
_analyzer: Optional[ContextAnalyzer] = None


def get_context_analyzer() -> ContextAnalyzer:
    """获取全局上下文分析器实例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ContextAnalyzer()
    return _analyzer
