[English](#english) | [中文](#中文)

---

# English

# AI Text Optimizer

A lightweight Windows desktop tool that sends selected text to AI for analysis and optimization. Supports multiple AI services, smart prompt templates, and bilingual interface.

## Features

- Global hotkey trigger
- Clipboard monitor mode
- Auto-detect source application
- Smart prompt templates
- Multiple AI service support
- Custom hotkey (press to set)
- System tray background run

## Installation

### Requirements

- Windows 10/11
- Python 3.8+

### Install dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| customtkinter | GUI framework |
| pynput | Global hotkey |
| pystray | System tray |
| requests | HTTP requests |
| pyperclip | Clipboard |
| Pillow | Image processing |

## Usage

### Start

```bash
python main.py
```

### Steps

1. Select text in any application
2. Press Ctrl+C to copy
3. Press hotkey (default: Ctrl+Shift+Q)
4. View AI analysis result

### Tray menu

Right-click the tray icon in system tray:

- Hotkey display - Click to open hotkey settings
- Hotkey ON/OFF
- Templates - Open template manager
- Settings - Open settings
- Language - Switch Chinese/English
- Quit

## Hotkey Settings

Supports "press to set" mode:

1. Click "Start Listening"
2. Press desired hotkey combination
3. Auto-saved

Press ESC to cancel.

Preset buttons available:
- Ctrl+Q
- Ctrl+Shift+Q
- Alt+Q

## Prompt Templates

### Built-in templates

| Template | Category | Description |
|----------|----------|-------------|
| [Bug] Code Fix | Code | Analyze error and provide fix |
| [Code] Optimize | Code | Optimize performance |
| [Code] Explain | Code | Explain code functionality |
| [Code] Review | Code | Code review with suggestions |
| [Bug] Debug | Debug | Debug and trace issues |
| [Bug] Stack Trace | Debug | Analyze stack traces |
| [Config] Fix | Config | Fix configuration issues |
| [Log] Analyze Log | Log | Analyze logs |
| [General] Translate | General | Translate text |
| [General] Summarize | General | Summarize content |

### Custom templates

1. Open template manager
2. Click "Add"
3. Fill in fields:
   - Key: unique identifier
   - Name: display name
   - Description
   - Category
   - Prompt content
4. Save

Available variables in prompt:
- `{text}` - Selected text
- `{source}` - Source application
- `{language}` - Programming language

## AI Service Configuration

### Supported services

| Service | Base URL | Models |
|---------|----------|--------|
| OpenAI | https://api.openai.com/v1 | gpt-4, gpt-3.5-turbo |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| Zhipu AI | https://open.bigmodel.cn/api/paas/v4 | glm-4 |
| Moonshot | https://api.moonshot.cn/v1 | moonshot-v1-8k |
| Qwen | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-turbo |
| Ollama (local) | http://localhost:11434/v1 | llama3 |
| Claude | https://api.anthropic.com/v1 | claude-3-sonnet |

### Setup steps

1. Right-click tray icon -> Settings
2. Select preset service or enter custom
3. Enter API Key
4. Click "Test Connection"
5. Save

## Configuration File

`config.json` - Main configuration file

```json
{
  "ai_service": {
    "provider": "openai_compatible",
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4"
  },
  "hotkey": {
    "trigger": "ctrl+shift+q",
    "enabled": true
  },
  "clipboard": {
    "wait_mode_timeout": 15,
    "check_interval": 0.2
  },
  "general": {
    "language": "auto",
    "enable_logging": false
  }
}
```

## Project Structure

```
ai-text-optimizer/
|-- main.py                  # Entry point
|-- config.py                # Configuration manager
|-- config.json              # Configuration file
|-- ai_service.py            # AI service adapter
|-- prompt_templates.py      # Prompt template manager
|-- context_analyzer.py      # Context analyzer
|-- clipboard.py             # Clipboard operations
|-- hotkey.py                # Hotkey listener
|-- text_cleaner.py          # Markdown cleaner
|-- language.py              # Multi-language support
|-- icons.py                 # Icon generator
|-- requirements.txt         # Dependencies
|-- README.md                # Documentation (English)
|-- README_zh.md             # Documentation (Chinese)
|-- ui/
|   |-- __init__.py
|   |-- floating_window.py   # Result window
|   |-- settings_window.py   # Settings window
|   |-- hotkey_window.py     # Hotkey settings
|   |-- template_window.py   # Template manager
|   |-- tray.py              # System tray
```

## FAQ

### Q: Hotkey not working?

A: Check if another application is using the same hotkey. Try setting a new hotkey via tray menu.

### Q: AI returns Markdown format?

A: The program automatically cleans Markdown. If it still appears, check if text_cleaner.py is working.

### Q: How to change language?

A: Right-click tray icon -> Language -> Select Chinese or English.

### Q: How to add custom prompt template?

A: Right-click tray icon -> Templates -> Click "Add" -> Fill in and save.

### Q: Which AI services are supported?

A: Any service compatible with OpenAI API format. See the service table above.

## License

MIT License

---

# 中文

# AI文本优化器

Windows桌面轻量工具，选中文本后发送给AI进行分析和优化。支持多种AI服务、智能提示词模板、中英文界面切换。

## 功能特点

- 全局热键触发
- 剪贴板监控模式
- 自动检测来源应用
- 智能提示词模板
- 多AI服务支持
- 自定义热键（按下即设）
- 系统托盘后台运行

## 安装

### 环境要求

- Windows 10/11
- Python 3.8+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 依赖列表

| 包名 | 用途 |
|------|------|
| customtkinter | GUI框架 |
| pynput | 全局热键 |
| pystray | 系统托盘 |
| requests | HTTP请求 |
| pyperclip | 剪贴板 |
| Pillow | 图像处理 |

## 使用方法

### 启动

```bash
python main.py
```

### 操作步骤

1. 在任意应用中选中文本
2. 按 Ctrl+C 复制
3. 按热键（默认 Ctrl+Shift+Q）
4. 查看AI分析结果

### 托盘菜单

右键点击系统托盘图标：

- 热键显示 - 点击打开热键设置
- 热键开关
- 提示词模板 - 打开模板管理
- 设置 - 打开设置
- 语言 - 切换中英文
- 退出

## 热键设置

支持"按下即设"模式：

1. 点击"开始监听"
2. 按下想要的热键组合
3. 自动保存

按ESC取消。

提供预设按钮：
- Ctrl+Q
- Ctrl+Shift+Q
- Alt+Q

## 提示词模板

### 内置模板

| 模板 | 分类 | 描述 |
|------|------|------|
| [Bug] 代码修复 | 代码 | 分析错误并提供修复方案 |
| [Code] 代码优化 | 代码 | 优化性能和可读性 |
| [Code] 代码解释 | 代码 | 解释代码功能 |
| [Code] 代码审查 | 代码 | 代码审查并提供建议 |
| [Bug] 调试追踪 | 调试 | 调试并追踪问题 |
| [Bug] 堆栈分析 | 调试 | 分析堆栈跟踪 |
| [Config] 配置修复 | 配置 | 修复配置问题 |
| [Log] 日志分析 | 日志 | 分析日志并定位问题 |
| [General] 翻译 | 通用 | 翻译文本 |
| [General] 总结 | 通用 | 总结内容要点 |

### 自定义模板

1. 打开模板管理器
2. 点击"添加"
3. 填写字段：
   - 标识：唯一标识符
   - 名称：显示名称
   - 描述
   - 分类
   - 提示词内容
4. 保存

提示词可用变量：
- `{text}` - 用户选中的文本
- `{source}` - 来源应用
- `{language}` - 编程语言

## AI服务配置

### 支持的服务

| 服务 | Base URL | 模型 |
|------|----------|------|
| OpenAI | https://api.openai.com/v1 | gpt-4, gpt-3.5-turbo |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| 智谱AI | https://open.bigmodel.cn/api/paas/v4 | glm-4 |
| 月之暗面 | https://api.moonshot.cn/v1 | moonshot-v1-8k |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-turbo |
| Ollama（本地） | http://localhost:11434/v1 | llama3 |
| Claude | https://api.anthropic.com/v1 | claude-3-sonnet |

### 设置步骤

1. 右键托盘图标 -> 设置
2. 选择预设服务或自定义
3. 输入API密钥
4. 点击"测试连接"
5. 保存

## 配置文件

`config.json` - 主配置文件

```json
{
  "ai_service": {
    "provider": "openai_compatible",
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4"
  },
  "hotkey": {
    "trigger": "ctrl+shift+q",
    "enabled": true
  },
  "clipboard": {
    "wait_mode_timeout": 15,
    "check_interval": 0.2
  },
  "general": {
    "language": "auto",
    "enable_logging": false
  }
}
```

## 项目结构

```
ai-text-optimizer/
|-- main.py                  # 主程序入口
|-- config.py                # 配置管理
|-- config.json              # 配置文件
|-- ai_service.py            # AI服务适配层
|-- prompt_templates.py      # 提示词模板管理
|-- context_analyzer.py      # 上下文分析器
|-- clipboard.py             # 剪贴板操作
|-- hotkey.py                # 热键监听
|-- text_cleaner.py          # Markdown清理
|-- language.py              # 多语言支持
|-- icons.py                 # 图标生成
|-- requirements.txt         # 依赖列表
|-- README.md                # 文档（英文）
|-- README_zh.md             # 文档（中文）
|-- ui/
|   |-- __init__.py
|   |-- floating_window.py   # 结果窗口
|   |-- settings_window.py   # 设置窗口
|   |-- hotkey_window.py     # 热键设置窗口
|   |-- template_window.py   # 模板管理窗口
|   |-- tray.py              # 系统托盘
```

## 常见问题

### Q: 热键不工作？

A: 检查是否有其他应用占用了相同热键。尝试通过托盘菜单设置新热键。

### Q: AI返回Markdown格式？

A: 程序会自动清理Markdown格式。如果仍然出现，检查text_cleaner.py是否正常工作。

### Q: 如何切换语言？

A: 右键托盘图标 -> 语言 -> 选择中文或English。

### Q: 如何添加自定义提示词模板？

A: 右键托盘图标 -> 提示词模板 -> 点击"添加" -> 填写并保存。

### Q: 支持哪些AI服务？

A: 任何兼容OpenAI API格式的服务。见上方服务表格。

## 许可证

MIT License
