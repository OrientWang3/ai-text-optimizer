"""
剪贴板操作模块 - 改进版
"""

import time
import threading
from typing import Optional
import ctypes
import pyperclip


class ClipboardManager:
    """剪贴板管理器"""

    def __init__(self):
        self._lock = threading.Lock()
        self.user32 = ctypes.windll.user32

    def get_selected_text(self) -> Optional[str]:
        """
        获取选中文本

        Windows限制：鼠标选中的文本不会自动进入剪贴板
        必须通过Ctrl+C或右键复制才能获取

        程序会尝试模拟Ctrl+C，如果失败则读取剪贴板
        """
        with self._lock:
            # 保存原始剪贴板
            original = self._get_clipboard()

            # 清空剪贴板（用于检测是否有新内容）
            pyperclip.copy('')
            time.sleep(0.05)

            # 模拟 Ctrl+C
            self._press_ctrl_c()

            # 等待剪贴板更新
            time.sleep(0.3)

            # 获取新内容
            selected = self._get_clipboard()

            # 如果没获取到，再等一下
            if not selected:
                time.sleep(0.2)
                selected = self._get_clipboard()

            # 检查是否有新内容
            if selected and selected.strip():
                # 有新内容，说明Ctrl+C成功
                return selected

            # Ctrl+C没有产生新内容
            # 可能是：
            # 1. 没有选中文本
            # 2. 程序阻止了Ctrl+C
            # 3. 用户需要先手动复制

            # 恢复原始内容
            if original:
                pyperclip.copy(original)

            return None

    def get_clipboard_text(self) -> Optional[str]:
        """直接获取剪贴板内容"""
        try:
            content = pyperclip.paste()
            return content if content and content.strip() else None
        except:
            return None

    def _press_ctrl_c(self):
        """模拟 Ctrl+C"""
        VK_CONTROL = 0x11
        VK_C = 0x43
        KEYUP = 0x0002

        # 按下 Ctrl
        self.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)

        # 按下 C
        self.user32.keybd_event(VK_C, 0, 0, 0)
        time.sleep(0.02)

        # 释放 C
        self.user32.keybd_event(VK_C, 0, KEYUP, 0)
        time.sleep(0.02)

        # 释放 Ctrl
        self.user32.keybd_event(VK_CONTROL, 0, KEYUP, 0)

    def _get_clipboard(self) -> str:
        try:
            content = pyperclip.paste()
            return content if content else ""
        except:
            return ""

    def set_content(self, text: str) -> bool:
        try:
            pyperclip.copy(text)
            return True
        except:
            return False


class TextSelector:
    """文本选择器"""

    def __init__(self):
        self._clipboard = ClipboardManager()
        self._last_selected = None

    def get_selection(self) -> Optional[str]:
        """获取选中文本"""
        text = self._clipboard.get_selected_text()

        if text:
            self._last_selected = text
        return text

    def get_last_selected(self) -> Optional[str]:
        return self._last_selected

    def copy_to_clipboard(self, text: str) -> bool:
        return self._clipboard.set_content(text)


_text_selector = None

def get_text_selector() -> TextSelector:
    global _text_selector
    if _text_selector is None:
        _text_selector = TextSelector()
    return _text_selector
