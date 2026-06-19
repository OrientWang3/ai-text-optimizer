"""
提示词模板管理器
默认提示词全部中文
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class PromptTemplate:
    """提示词模板"""

    def __init__(self, name: str, description: str, prompt: str, category: str = "custom", name_key: str = None, desc_key: str = None):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.category = category
        self.name_key = name_key
        self.desc_key = desc_key

    def get_display_name(self) -> str:
        """获取显示名称（支持翻译）"""
        if self.name_key:
            from language import t
            translated = t(self.name_key)
            if translated != self.name_key:
                return translated
        return self.name

    def get_display_desc(self) -> str:
        """获取显示描述（支持翻译）"""
        if self.desc_key:
            from language import t
            translated = t(self.desc_key)
            if translated != self.desc_key:
                return translated
        return self.description

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PromptTemplate':
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            prompt=data.get("prompt", ""),
            category=data.get("category", "custom")
        )


class PromptTemplateManager:
    """提示词模板管理器"""

    # 预设模板 - 全部中文提示词
    BUILTIN_TEMPLATES = {
        "code_fix": PromptTemplate(
            name="[Bug] 代码修复",
            name_key="tpl_code_fix",
            description="分析错误并提供修复方案",
            desc_key="tpl_code_fix_desc",
            category="code",
            prompt="""你是一个代码调试专家。请分析以下错误并提供修复方案。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的分析和建议
4. 代码直接写出来，用缩进表示层级

来源: {source}
语言: {language}
错误/代码:
{text}

请直接提供：
1. 错误原因：一句话说明为什么会报错
2. 修复代码：直接给出修改后的代码
3. 修改说明：简要说明改了哪里

回答要简洁直接，重点是代码修复。"""
        ),

        "code_optimize": PromptTemplate(
            name="[Code] 代码优化",
            name_key="tpl_code_optimize",
            description="优化代码性能和可读性",
            desc_key="tpl_code_optimize_desc",
            category="code",
            prompt="""你是一个代码优化专家。请分析以下代码并提供优化版本。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的分析和优化代码
4. 代码直接写出来，用缩进表示层级

来源: {source}
语言: {language}
原始代码:
{text}

请直接提供：
1. 优化后的代码：直接给出改进后的完整代码
2. 改进点：列出主要的优化内容
3. 注意事项：使用新代码时需要注意什么

回答要简洁，重点是提供可直接使用的优化代码。"""
        ),

        "code_explain": PromptTemplate(
            name="[Code] 代码解释",
            name_key="tpl_code_explain",
            description="解释代码功能",
            desc_key="tpl_code_explain_desc",
            category="code",
            prompt="""你是一个代码文档专家。请解释以下代码的功能。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的解释

来源: {source}
语言: {language}
代码:
{text}

请提供：
1. 功能说明：这段代码做了什么
2. 核心逻辑：关键步骤解释
3. 输入输出：接受什么参数，返回什么结果
4. 使用示例：如何调用

请清晰易懂地解释。"""
        ),

        "code_review": PromptTemplate(
            name="[Code] 代码审查",
            name_key="tpl_code_review",
            description="代码审查并提供建议",
            desc_key="tpl_code_review_desc",
            category="code",
            prompt="""你是一个资深开发者。请审查以下代码并提供反馈。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的审查意见
4. 代码直接写出来，用缩进表示层级

来源: {source}
语言: {language}
代码:
{text}

请提供：
1. 整体评价：代码质量如何
2. 问题列表：列出bug、安全隐患或不良实践
3. 改进建议：优化建议
4. 重构代码：如有需要，提供改进后的代码

请具体且有建设性地反馈。"""
        ),

        "bug_debug": PromptTemplate(
            name="[Bug] 调试追踪",
            name_key="tpl_bug_debug",
            description="调试并追踪问题",
            desc_key="tpl_bug_debug_desc",
            category="debug",
            prompt="""你是一个调试专家。请帮助追踪和调试以下问题。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的分析和建议

来源: {source}
问题描述:
{text}

请提供：
1. 问题分析：哪里出了问题
2. 调试步骤：如何排查这个问题
3. 可能原因：列出可能的原因
4. 解决方案：如何修复

请系统性地分析和解决。"""
        ),

        "bug_stack": PromptTemplate(
            name="[Bug] 堆栈分析",
            name_key="tpl_bug_stack",
            description="分析堆栈跟踪信息",
            desc_key="tpl_bug_stack_desc",
            category="debug",
            prompt="""你是一个堆栈跟踪分析专家。请分析以下堆栈信息并找到根本原因。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的分析和修复方案
4. 代码直接写出来，用缩进表示层级

堆栈跟踪:
{text}

请提供：
1. 根本原因：错误的真正原因
2. 调用链：错误是如何传播的
3. 修复位置：应该在哪里修改
4. 修复代码：具体的修复方案

请准确指出文件名和行号（如果有的话）。"""
        ),

        "config_fix": PromptTemplate(
            name="[Config] 配置修复",
            name_key="tpl_config_fix",
            description="修复配置问题",
            desc_key="tpl_config_fix_desc",
            category="config",
            prompt="""你是一个配置专家。请分析并修复以下配置问题。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的分析和修复配置
4. 配置直接写出来，用缩进表示层级

来源: {source}
配置内容:
{text}

请提供：
1. 问题说明：配置有什么问题
2. 修复后的配置：直接给出正确的配置
3. 修改说明：改了什么，为什么改
4. 验证方法：如何确认修复生效

请提供可直接使用的配置。"""
        ),

        "log_analyze": PromptTemplate(
            name="[Log] 日志分析",
            name_key="tpl_log_analyze",
            description="分析日志并定位问题",
            desc_key="tpl_log_analyze_desc",
            category="log",
            prompt="""你是一个日志分析专家。请分析以下日志并找出问题。

重要规则：
1. 用纯文本回答，不要用Markdown（不要**加粗**、不要```代码块```、不要#标题）
2. 不要重复用户发送的原文内容
3. 只输出你的分析和建议

来源: {source}
日志内容:
{text}

请提供：
1. 摘要：发生了什么
2. 发现的问题：列出错误或警告
3. 时间线：关键事件顺序
4. 建议：下一步该怎么做

请简洁且可操作。"""
        ),

        "translate": PromptTemplate(
            name="[General] 翻译",
            name_key="tpl_translate",
            description="翻译文本",
            desc_key="tpl_translate_desc",
            category="general",
            prompt="""请翻译以下文本。如果是代码，请只翻译注释部分。

重要规则：
1. 用纯文本回答，不要用Markdown
2. 不要重复用户发送的原文内容
3. 只输出翻译结果

待翻译文本:
{text}

请直接提供翻译结果。"""
        ),

        "summarize": PromptTemplate(
            name="[General] 总结",
            name_key="tpl_summarize",
            description="总结内容要点",
            desc_key="tpl_summarize_desc",
            category="general",
            prompt="""请简洁总结以下内容的要点。

重要规则：
1. 用纯文本回答，不要用Markdown
2. 不要重复用户发送的原文内容
3. 只输出你的总结

内容:
{text}

请提供简要总结和关键要点。"""
        ),
    }

    def __init__(self, templates_path: str = "prompt_templates.json"):
        self.templates_path = Path(templates_path)
        self.templates: Dict[str, PromptTemplate] = {}

        # 加载内置模板
        self.templates.update(self.BUILTIN_TEMPLATES)

        # 加载自定义模板
        self._load_custom_templates()

    def _load_custom_templates(self):
        try:
            if self.templates_path.exists():
                with open(self.templates_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, template_data in data.items():
                        self.templates[key] = PromptTemplate.from_dict(template_data)
        except Exception as e:
            print(f"[Templates] Load error: {e}")

    def save_custom_templates(self):
        try:
            custom_templates = {}
            for key, template in self.templates.items():
                if key not in self.BUILTIN_TEMPLATES:
                    custom_templates[key] = template.to_dict()

            with open(self.templates_path, 'w', encoding='utf-8') as f:
                json.dump(custom_templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Templates] Save error: {e}")

    def get_template(self, key: str) -> Optional[PromptTemplate]:
        return self.templates.get(key)

    def get_all_templates(self) -> Dict[str, PromptTemplate]:
        return self.templates.copy()

    def get_templates_by_category(self) -> Dict[str, List[Dict]]:
        categories = {}
        for key, template in self.templates.items():
            cat = template.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "key": key,
                "name": template.get_display_name(),
                "description": template.get_display_desc()
            })
        return categories

    def get_template_names(self) -> List[str]:
        return [t.get_display_name() for t in self.templates.values()]

    def get_template_keys(self) -> List[str]:
        return list(self.templates.keys())

    def add_template(self, key: str, name: str, description: str, prompt: str, category: str = "custom") -> bool:
        """添加模板"""
        print(f"[Templates] Adding: key={key}, name={name}")

        if key in self.BUILTIN_TEMPLATES:
            print(f"[Templates] Cannot override builtin: {key}")
            return False

        if key in self.templates:
            print(f"[Templates] Already exists: {key}")
            return False

        self.templates[key] = PromptTemplate(
            name=name,
            description=description,
            prompt=prompt,
            category=category
        )

        self.save_custom_templates()
        print(f"[Templates] Added: {key}")
        return True

    def update_template(self, key: str, name: str = None, description: str = None, prompt: str = None) -> bool:
        if key not in self.templates:
            return False

        template = self.templates[key]
        if name:
            template.name = name
        if description:
            template.description = description
        if prompt:
            template.prompt = prompt

        self.save_custom_templates()
        return True

    def delete_template(self, key: str) -> bool:
        if key in self.BUILTIN_TEMPLATES:
            return False

        if key in self.templates:
            del self.templates[key]
            self.save_custom_templates()
            return True
        return False

    def format_prompt(self, key: str, text: str, source: str = "Unknown", language: str = "") -> Optional[str]:
        template = self.templates.get(key)
        if not template:
            return None

        return template.prompt.format(
            text=text,
            source=source,
            language=language
        )


# 全局实例
_template_manager: Optional[PromptTemplateManager] = None


def get_template_manager() -> PromptTemplateManager:
    global _template_manager
    if _template_manager is None:
        _template_manager = PromptTemplateManager()
    return _template_manager
