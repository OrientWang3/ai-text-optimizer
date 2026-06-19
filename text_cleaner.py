"""
文本清理模块 - 去除Markdown格式
"""

import re


def clean_markdown(text: str) -> str:
    """
    清理Markdown格式，转换为纯文本

    Args:
        text: 包含Markdown的文本

    Returns:
        清理后的纯文本
    """
    if not text:
        return text

    # 1. 处理代码块 (```...```)
    # 保留代码内容，去掉标记
    text = re.sub(r'```[\w]*\n?', '', text)
    text = re.sub(r'```', '', text)

    # 2. 处理行内代码 (`...`)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # 3. 处理标题 (# ## ### 等)
    # 转换为 [标题] 格式
    text = re.sub(r'^#{1}\s+(.+)$', r'[\1]', text, flags=re.MULTILINE)
    text = re.sub(r'^#{2}\s+(.+)$', r'[\1]', text, flags=re.MULTILINE)
    text = re.sub(r'^#{3,}\s+(.+)$', r'[\1]', text, flags=re.MULTILINE)

    # 4. 处理加粗 (**...**)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)

    # 5. 处理斜体 (*...*)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # 6. 处理链接 ([text](url))
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # 7. 处理列表标记 (- * +)
    # 保留内容，用 > 表示列表项
    text = re.sub(r'^[\s]*[-*+]\s+', '  > ', text, flags=re.MULTILINE)

    # 8. 处理有序列表 (1. 2. 等)
    text = re.sub(r'^[\s]*\d+\.\s+', '  ', text, flags=re.MULTILINE)

    # 9. 处理引用 (>)
    text = re.sub(r'^[\s]*>\s+', '  ', text, flags=re.MULTILINE)

    # 10. 处理水平线 (--- ***)
    text = re.sub(r'^[-*_]{3,}$', '─' * 40, text, flags=re.MULTILINE)

    # 11. 清理多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 12. 清理行首行尾空格
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    text = '\n'.join(lines)

    return text.strip()


def format_for_display(text: str) -> str:
    """
    格式化文本用于显示

    Args:
        text: 原始文本

    Returns:
        格式化后的文本
    """
    # 先清理Markdown
    text = clean_markdown(text)

    # 确保有适当的换行
    text = text.replace('\r\n', '\n')

    return text


# 测试
if __name__ == "__main__":
    test = """### 内容分析

- **内容**：`python main.py`
- **来源**：`python.exe`

```bash
python main.py
```

1. **指定 Python 版本**
   使用 `python3`
"""

    print("Before:")
    print(test)
    print("\n" + "="*50 + "\n")
    print("After:")
    print(clean_markdown(test))
