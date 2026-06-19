"""
热键设置窗口 - 按下热键方式
"""

import customtkinter as ctk
from typing import Optional, Callable
from config import get_config
from language import t
from icons import get_icon_manager
from pynput import keyboard
from pynput.keyboard import Key, KeyCode


class HotkeyWindow:
    """热键设置窗口 - 按下热键方式"""

    def __init__(self):
        self.config = get_config()
        self._window: Optional[ctk.CTkToplevel] = None
        self._is_visible = False
        self._on_close: Optional[Callable] = None
        self._on_save: Optional[Callable] = None
        self._icons = get_icon_manager()

        # 监听状态
        self._listening = False
        self._listener = None
        self._pressed_keys = set()

        # UI组件
        self._status_label = None
        self._preview_label = None
        self._listen_btn = None

    def _create_window(self) -> None:
        if self._window is not None:
            return

        self._window = ctk.CTkToplevel()
        self._window.title(t("hotkey_title"))
        self._window.geometry("450x400")
        self._window.attributes("-topmost", True)
        self._window.resizable(False, False)

        self._center_window()
        self._create_widgets()
        self._window.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _center_window(self) -> None:
        if self._window is None:
            return
        sw = self._window.winfo_screenwidth()
        sh = self._window.winfo_screenheight()
        x = (sw - 450) // 2
        y = (sh - 400) // 2
        self._window.geometry(f"450x400+{x}+{y}")

    def _create_widgets(self) -> None:
        if self._window is None:
            return

        main = ctk.CTkFrame(self._window, fg_color="#1e1e2e")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # 标题
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        settings_icon = self._icons.create_icon("settings", size=22, color="#cba6f7")
        ctk.CTkLabel(
            header,
            image=settings_icon,
            text=f" {t('hotkey_title')}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#cba6f7",
            compound="left"
        ).pack(side="left")

        # 当前热键
        current_frame = ctk.CTkFrame(main, fg_color="#313244", corner_radius=8)
        current_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            current_frame,
            text=t("hotkey_current") + ":",
            font=ctk.CTkFont(size=12),
            text_color="#a6adc8"
        ).pack(padx=15, pady=(10, 5))

        current_hotkey = self.config.get_hotkey().upper().replace("+", " + ")
        ctk.CTkLabel(
            current_frame,
            text=current_hotkey,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#89b4fa"
        ).pack(padx=15, pady=(0, 15))

        # 监听区域
        listen_frame = ctk.CTkFrame(main, fg_color="#181825", corner_radius=10)
        listen_frame.pack(fill="x", pady=(0, 20))

        # 说明文字
        ctk.CTkLabel(
            listen_frame,
            text=t("hotkey_press"),
            font=ctk.CTkFont(size=14),
            text_color="#cdd6f4"
        ).pack(pady=(15, 10))

        ctk.CTkLabel(
            listen_frame,
            text=t("hotkey_example"),
            font=ctk.CTkFont(size=11),
            text_color="#6c7086"
        ).pack(pady=(0, 10))

        # 预览标签
        self._preview_label = ctk.CTkLabel(
            listen_frame,
            text=t("hotkey_waiting"),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f9e2af"
        )
        self._preview_label.pack(pady=(0, 10))

        # 状态标签
        self._status_label = ctk.CTkLabel(
            listen_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#a6adc8"
        )
        self._status_label.pack(pady=(0, 5))

        # 监听按钮
        self._listen_btn = ctk.CTkButton(
            listen_frame,
            text=t("hotkey_start_listen"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=200,
            fg_color="#f38ba8",
            hover_color="#eba0ac",
            text_color="#1e1e2e",
            command=self._toggle_listen,
            corner_radius=8
        )
        self._listen_btn.pack(pady=(5, 20))

        # 底部按钮
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        # 预设按钮
        preset_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        preset_frame.pack(side="left")

        ctk.CTkLabel(
            preset_frame,
            text="预设:",
            font=ctk.CTkFont(size=11),
            text_color="#6c7086"
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            preset_frame,
            text="Ctrl+Q",
            font=ctk.CTkFont(size=11),
            height=28,
            width=70,
            fg_color="#45475a",
            hover_color="#585b70",
            command=lambda: self._set_preset("ctrl+q"),
            corner_radius=4
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            preset_frame,
            text="Ctrl+Shift+Q",
            font=ctk.CTkFont(size=11),
            height=28,
            width=100,
            fg_color="#45475a",
            hover_color="#585b70",
            command=lambda: self._set_preset("ctrl+shift+q"),
            corner_radius=4
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            preset_frame,
            text="Alt+Q",
            font=ctk.CTkFont(size=11),
            height=28,
            width=70,
            fg_color="#45475a",
            hover_color="#585b70",
            command=lambda: self._set_preset("alt+q"),
            corner_radius=4
        ).pack(side="left", padx=2)

        # 关闭按钮
        ctk.CTkButton(
            btn_frame,
            text=t("close"),
            font=ctk.CTkFont(size=13),
            height=35,
            width=80,
            fg_color="#585b70",
            hover_color="#45475a",
            command=self._on_window_close,
            corner_radius=6
        ).pack(side="right")

    def _toggle_listen(self):
        """切换监听状态"""
        if self._listening:
            self._stop_listen()
        else:
            self._start_listen()

    def _start_listen(self):
        """开始监听"""
        self._listening = True
        self._pressed_keys = set()

        self._listen_btn.configure(
            text=t("hotkey_stop_listen"),
            fg_color="#a6e3a1",
            hover_color="#94e2d5"
        )
        self._preview_label.configure(text=t("hotkey_waiting"), text_color="#f9e2af")
        self._status_label.configure(text=t("hotkey_press_esc"), text_color="#6c7086")

        # 启动键盘监听
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.start()

    def _stop_listen(self):
        """停止监听"""
        self._listening = False

        if self._listener:
            self._listener.stop()
            self._listener = None

        self._listen_btn.configure(
            text=t("hotkey_start_listen"),
            fg_color="#f38ba8",
            hover_color="#eba0ac"
        )
        self._status_label.configure(text="")

    def _on_key_press(self, key):
        """按键按下"""
        if not self._listening:
            return

        # ESC取消
        if key == Key.esc:
            self._window.after(0, self._stop_listen)
            self._window.after(0, lambda: self._preview_label.configure(text=t("hotkey_cancelled"), text_color="#f38ba8"))
            return

        self._pressed_keys.add(key)

        # 构建热键字符串
        parts = []

        # 检查修饰键
        ctrl = Key.ctrl_l in self._pressed_keys or Key.ctrl_r in self._pressed_keys
        shift = Key.shift_l in self._pressed_keys or Key.shift_r in self._pressed_keys
        alt = Key.alt_l in self._pressed_keys or Key.alt_r in self._pressed_keys

        if ctrl:
            parts.append("Ctrl")
        if shift:
            parts.append("Shift")
        if alt:
            parts.append("Alt")

        # 检查普通键
        normal_key = None
        for k in self._pressed_keys:
            if k not in (Key.ctrl_l, Key.ctrl_r, Key.shift_l, Key.shift_r, Key.alt_l, Key.alt_r):
                if hasattr(k, 'char') and k.char:
                    normal_key = k.char.upper()
                elif hasattr(k, 'name'):
                    normal_key = k.name.upper()
                break

        if normal_key:
            parts.append(normal_key)

        # 更新预览
        if parts:
            hotkey_str = " + ".join(parts)
            self._window.after(0, lambda: self._preview_label.configure(
                text=hotkey_str,
                text_color="#a6e3a1"
            ))

            # 如果有普通键且有修饰键，保存
            if normal_key and (ctrl or shift or alt):
                # 构建保存格式
                save_parts = []
                if ctrl:
                    save_parts.append("ctrl")
                if shift:
                    save_parts.append("shift")
                if alt:
                    save_parts.append("alt")
                save_parts.append(normal_key.lower())

                hotkey_save = "+".join(save_parts)

                # 延迟保存
                self._window.after(500, lambda: self._save_hotkey(hotkey_save))

    def _on_key_release(self, key):
        """按键释放"""
        if not self._listening:
            return

        self._pressed_keys.discard(key)

    def _save_hotkey(self, hotkey: str):
        """保存热键"""
        self._stop_listen()

        # 保存到配置
        self.config.set("hotkey.trigger", hotkey)
        self.config.save()

        # 更新显示
        display = hotkey.upper().replace("+", " + ")
        self._preview_label.configure(text=f"✓ {display}", text_color="#a6e3a1")
        self._status_label.configure(text=t("hotkey_saved"), text_color="#a6e3a1")

        # 回调
        if self._on_save:
            self._on_save(hotkey)

    def _set_preset(self, hotkey: str):
        """设置预设热键"""
        display = hotkey.upper().replace("+", " + ")
        self._preview_label.configure(text=display, text_color="#a6e3a1")

        # 保存
        self.config.set("hotkey.trigger", hotkey)
        self.config.save()

        self._status_label.configure(text="热键已更新！", text_color="#a6e3a1")

        if self._on_save:
            self._on_save(hotkey)

    def _on_window_close(self):
        """关闭窗口"""
        self._stop_listen()
        self.close()
        if self._on_close:
            self._on_close()

    def show(self):
        """显示窗口"""
        if self._window is None:
            self._create_window()
        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()
        self._is_visible = True

    def close(self):
        """关闭窗口"""
        self._stop_listen()
        if self._window:
            self._window.destroy()
            self._window = None
            self._is_visible = False

    def set_on_close(self, callback):
        self._on_close = callback

    def set_on_save(self, callback):
        self._on_save = callback

    def is_visible(self):
        return self._is_visible


_hotkey_window = None

def get_hotkey_window():
    global _hotkey_window
    if _hotkey_window is None:
        _hotkey_window = HotkeyWindow()
    return _hotkey_window
