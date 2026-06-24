<p align="center">
<h1 align="center">AI 文本优化器</h1>
</p>
<p align="center">
  <a href="https://img.shields.io/badge/version-v1.0.1-blue">
    <img alt="version" src="https://img.shields.io/badge/version-v1.0.1-blue?color=009922" />
  </a>
  <a>
    <img alt="platform" src="https://img.shields.io/badge/platform-Windows-blue?color=0078D6" />
  </a>
  <a>
    <img alt="license" src="https://img.shields.io/badge/license-MIT-red" />
  </a>
  <a>
    <img alt="PRs-Welcome" src="https://img.shields.io/badge/PRs-Welcome-green" />
  </a>
  <br />
</p>

<div align="center">
<p align="center">
  <a href="#项目动机">项目动机</a>/
  <a href="#核心设计">核心设计</a>/
  <a href="#快速开始">快速开始</a>/
  <a href="#项目结构">项目结构</a>/
  <a href="#常见问题">常见问题</a>
</p>
</div>

## 项目动机

在日常工作中，我们经常遇到这样的场景：代码报错了要排查、英文邮件要润色、技术文档要翻译。传统的做法是：选中文本 → 打开浏览器 → 粘贴到 ChatGPT → 等待回复 → 复制回来 → 粘贴回去。这个流程打断了工作节奏，频繁切换窗口让人烦躁。

有没有可能：选中文字，按一个键，AI 帮你处理好，直接粘贴回去？

这就是这个工具的初衷。它不是一个"AI 套壳"，而是一个**系统级的生产力工具**——常驻托盘、全局热键、在任何应用中随叫随到。

## 核心设计

### 工作流程

```
选中文本 → 按 Ctrl+Shift+Q → AI 分析 → 结果弹窗 → 一键复制
```

整个过程不离开当前应用，不打开浏览器，不切换窗口。

### 智能上下文感知

不同于简单地"把选中文本发给 AI"，本工具在发送前会自动分析：

| 分析维度 | 说明 | 用途 |
|---------|------|------|
| 来源应用 | 检测当前前台窗口（VS Code、Chrome、终端等） | 针对性调整提示词 |
| 内容类型 | 分类为错误、代码、日志、配置、普通文本 | 自动匹配内置模板 |
| 编程语言 | 识别 Python、JS、Java、Go 等 10+ 语言 | 提示词中告知 AI 语言上下文 |

分析结果决定使用哪套内置提示词，用户无需手动选择模板。

### 多 AI 后端支持

| 服务商 | 模型示例 | 备注 |
|--------|---------|------|
| OpenAI | GPT-4、GPT-4-turbo、GPT-3.5-turbo | 兼容 OpenAI API |
| DeepSeek | deepseek-chat、deepseek-coder | 高性价比 |
| 智谱 AI | GLM-4、GLM-4-flash | 国产模型 |
| 月之暗面 | moonshot-v1-8k/32k/128k | 超长上下文 |
| 通义千问 | qwen-turbo、qwen-plus、qwen-max | 阿里云 |
| Claude | claude-3-opus/sonnet | Anthropic |
| Ollama | llama3、codellama、mistral | 本地部署，免费 |

任何兼容 OpenAI `/v1/chat/completions` 接口的服务均可接入。

### 内置提示词模板

预置 10 个场景模板，覆盖日常开发需求：

| 模板 | 分类 | 用途 |
|------|------|------|
| 代码修复 | 代码 | 分析报错并给出修复代码 |
| 代码优化 | 代码 | 优化性能和可读性 |
| 代码解释 | 代码 | 解释代码功能和逻辑 |
| 代码审查 | 代码 | 审查代码质量并给出建议 |
| 调试追踪 | 调试 | 系统性排查问题 |
| 堆栈分析 | 调试 | 解析堆栈跟踪，定位根因 |
| 配置修复 | 配置 | 诊断并修复配置文件问题 |
| 日志分析 | 日志 | 从日志中提取关键信息 |
| 翻译 | 通用 | 翻译选中文本 |
| 总结 | 通用 | 提取内容要点 |

所有模板支持通过界面增删改，使用 `{text}`、`{source}`、`{language}` 三个变量。

## 快速开始

### 环境要求

- Windows 10/11
- Python 3.10+

### 安装

```bash
git clone https://github.com/yourusername/ai-text-optimizer.git
cd ai-text-optimizer
pip install -r requirements.txt
```

### 配置

```bash
cp config.example.json config.json
```

编辑 `config.json`，填入 API 信息：

```json
{
  "ai_service": {
    "provider": "openai_compatible",
    "api_key": "你的API密钥",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4"
  },
  "hotkey": {
    "trigger": "ctrl+shift+q"
  }
}
```

也可以启动后右键托盘图标 → 设置，通过图形界面配置。

### 启动

```bash
python main.py
```

托盘图标出现在右下角，按 `Ctrl+Shift+Q` 即可使用。

### 打包为 EXE

```bash
pip install pyinstaller
python build.py
```

输出文件：`dist/AI文本优化器.exe`

## 项目结构

```
ai-text-optimizer/
├── main.py                   # 应用入口，生命周期管理
├── config.py                 # 配置管理（JSON 存储，点号路径读写）
├── ai_service.py             # AI 服务适配层（OpenAI / Claude 双协议）
├── prompt_templates.py       # 提示词模板管理器（内置 + 自定义）
├── context_analyzer.py       # 上下文分析（窗口检测 + 文本分类）
├── clipboard.py              # 剪贴板操作（Ctrl+C 模拟 + 内容读取）
├── hotkey.py                 # 全局热键监听（pynput，动态键位）
├── text_cleaner.py           # Markdown → 纯文本转换
├── language.py               # 中英双语支持
├── logger.py                 # 结构化日志（控制台 + 文件）
├── icons.py                  # 程序化图标生成（Pillow）
├── build.py                  # PyInstaller 打包脚本
├── tests/                    # 单元测试（pytest，29 个用例）
└── ui/
    ├── floating_window.py    # AI 结果浮动窗口
    ├── settings_window.py    # 设置界面（AI 配置 / 热键 / 语言）
    ├── hotkey_window.py      # "按下即设"热键录制
    ├── template_window.py    # 模板浏览 / 编辑 / 删除
    └── tray.py               # 系统托盘图标与菜单
```

## 常见问题

**Q: 热键不生效？**

检查是否有其他应用占用了相同组合键（如 QQ 截图 `Ctrl+Alt+A`）。右键托盘 → 热键设置 → 录制新的组合键。

**Q: AI 返回了 Markdown 格式？**

程序内置了 Markdown 清理器（`text_cleaner.py`），会自动去除 `**加粗**`、代码块标记、标题符号等。如果仍有残留，请提 Issue。

**Q: 支持哪些 AI 服务？**

任何兼容 OpenAI `/v1/chat/completions` 格式的服务，以及 Anthropic Claude API。Ollama 本地部署也可以。

**Q: 如何切换中英文界面？**

右键托盘图标 → 语言 → 选择中文或 English。首次启动会自动检测系统语言。

## 许可证

MIT License

## 免责声明

本工具需要用户自行提供 AI 服务的 API 密钥。请妥善保管你的密钥，不要将其提交到公开仓库。`config.json` 已加入 `.gitignore`。

---

如果这个工具对你有帮助，欢迎 Star ⭐
