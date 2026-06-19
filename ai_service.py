"""
AI服务适配层
支持多种AI服务提供商，使用智能提示词系统
"""

import requests
import json
from typing import Dict, List, Optional, Any
from config import get_config
from context_analyzer import get_context_analyzer, WindowContext, TextAnalysis
from text_cleaner import clean_markdown


class AIServiceError(Exception):
    """AI服务异常"""
    pass


class AIService:
    """统一AI服务接口"""

    # 预设的AI服务配置
    PRESET_SERVICES = {
        "openai": {
            "name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "provider": "openai_compatible"
        },
        "deepseek": {
            "name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-coder"],
            "provider": "openai_compatible"
        },
        "zhipu": {
            "name": "智谱AI (ChatGLM)",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4", "glm-4-flash", "glm-3-turbo"],
            "provider": "openai_compatible"
        },
        "moonshot": {
            "name": "月之暗面 (Kimi)",
            "base_url": "https://api.moonshot.cn/v1",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "provider": "openai_compatible"
        },
        "qwen": {
            "name": "阿里通义千问",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "provider": "openai_compatible"
        },
        "ollama": {
            "name": "本地 Ollama",
            "base_url": "http://localhost:11434/v1",
            "models": ["llama3", "codellama", "mistral"],
            "provider": "openai_compatible"
        },
        "claude": {
            "name": "Claude",
            "base_url": "https://api.anthropic.com/v1",
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
            "provider": "claude"
        }
    }

    def __init__(self):
        """初始化AI服务"""
        self.config = get_config()
        self.analyzer = get_context_analyzer()
        self._session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        api_key = self.config.get("ai_service.api_key", "")
        provider = self.config.get("ai_service.provider", "openai_compatible")

        if provider == "claude":
            return {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        else:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

    def _get_base_url(self) -> str:
        """获取API基础URL"""
        return self.config.get("ai_service.base_url", "https://api.openai.com/v1")

    def _get_model(self) -> str:
        """获取模型名称"""
        return self.config.get("ai_service.model", "gpt-4")

    def _get_max_tokens(self) -> int:
        """获取最大token数"""
        return self.config.get("ai_service.max_tokens", 4000)

    def _get_temperature(self) -> float:
        """获取温度参数"""
        return self.config.get("ai_service.temperature", 0.7)

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            stream: 是否使用流式响应

        Returns:
            AI响应内容

        Raises:
            AIServiceError: 请求失败时抛出异常
        """
        provider = self.config.get("ai_service.provider", "openai_compatible")

        if provider == "openai_compatible":
            return self._chat_openai_compatible(messages, stream)
        elif provider == "claude":
            return self._chat_claude(messages, stream)
        else:
            raise AIServiceError(f"不支持的AI服务提供商: {provider}")

    def _chat_openai_compatible(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """调用OpenAI兼容API"""
        base_url = self._get_base_url()
        url = f"{base_url}/chat/completions"

        payload = {
            "model": self._get_model(),
            "messages": messages,
            "max_tokens": self._get_max_tokens(),
            "temperature": self._get_temperature(),
            "stream": stream
        }

        try:
            response = self._session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"网络请求失败: {str(e)}")
        except KeyError as e:
            raise AIServiceError(f"响应格式错误: {str(e)}")
        except Exception as e:
            raise AIServiceError(f"未知错误: {str(e)}")

    def _chat_claude(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """调用Claude API"""
        base_url = self._get_base_url()
        url = f"{base_url}/messages"

        # 转换消息格式
        claude_messages = []
        system_message = None

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        payload = {
            "model": self._get_model(),
            "max_tokens": self._get_max_tokens(),
            "messages": claude_messages
        }

        if system_message:
            payload["system"] = system_message

        try:
            response = self._session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            return result["content"][0]["text"]

        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"网络请求失败: {str(e)}")
        except KeyError as e:
            raise AIServiceError(f"响应格式错误: {str(e)}")
        except Exception as e:
            raise AIServiceError(f"未知错误: {str(e)}")

    def analyze_and_optimize(self, text: str) -> Dict[str, Any]:
        """
        分析文本并使用AI优化

        Args:
            text: 要分析和优化的文本

        Returns:
            包含分析结果和AI响应的字典
        """
        # 1. 获取当前窗口上下文
        context = self.analyzer.get_active_window()

        # 2. 分析文本类型
        analysis = self.analyzer.analyze_text(text, context)

        # 3. 生成智能提示词
        smart_prompt = self.analyzer.generate_smart_prompt(text, analysis, context)

        # 4. 调用AI
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的技术助手，擅长分析错误、代码、日志和配置。
请用清晰、简洁的纯文本格式回答。
不要使用Markdown语法（不要用**加粗**、不要用```代码块```、不要用#标题、不要用- 列表）。
代码直接写出来，用缩进表示层级。
用数字编号（1. 2. 3.）来组织要点。"""
            },
            {
                "role": "user",
                "content": smart_prompt
            }
        ]

        ai_response = self.chat(messages)

        # 5. 清理Markdown格式（以防万一）
        ai_response = clean_markdown(ai_response)

        return {
            "context": context,
            "analysis": analysis,
            "prompt": smart_prompt,
            "response": ai_response
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        测试API连接

        Returns:
            测试结果
        """
        try:
            messages = [
                {"role": "user", "content": "Hello, please respond with 'OK' to confirm the connection."}
            ]
            response = self.chat(messages)
            return {
                "success": True,
                "message": "连接成功",
                "response": response[:100] + "..." if len(response) > 100 else response
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接失败: {str(e)}"
            }

    @classmethod
    def get_preset_services(cls) -> Dict[str, Dict]:
        """获取预设服务列表"""
        return cls.PRESET_SERVICES

    @classmethod
    def get_preset_service(cls, service_id: str) -> Optional[Dict]:
        """获取指定预设服务"""
        return cls.PRESET_SERVICES.get(service_id)


# 全局AI服务实例
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """获取全局AI服务实例"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


def reload_ai_service() -> AIService:
    """重新加载AI服务"""
    global _ai_service
    _ai_service = AIService()
    return _ai_service
