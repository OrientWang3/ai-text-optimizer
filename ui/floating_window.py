"""
浮动窗口模块 - 支持多语言
"""

import customtkinter as ctk
from typing import Optional, Callable
from config import get_config
from language import t
from icons import get_icon_manager


class FloatingWindow:
    """浮动结果窗口"""

    TYPE_ICONS = {
        "error": "error",
        "code": "code",
        "log": "log",
        "config": "config",
        "plain": "text",
    }

    APP_ICONS = {
        "editor": "code",
        "browser": "source",
        "terminal": "log",
        "messaging": "text",
        "ai": "ai",
        "other": "source",
    }

    def __init__(self):
        self.config = get_config()
        self._window: Optional[ctk.CTkToplevel] = None
        self._is_visible = False
        self._on_close: Optional[Callable] = None
        self._on_copy: Optional[Callable[[str], None]] = None
        self._icons = get_icon_manager()

        self._app_label = None
        self._type_label = None
        self._original_text = None
        self._result_text = None
        self._copy_btn = None
        self._copy_orig_btn = None
        self._close_btn = None
        self._status_label = None
        self._orig_header_label = None
        self._result_header_label = None

    def _create_window(self) -> None:
        if self._window is not None:
            return

        self._window = ctk.CTkToplevel()
        self._window.title(t("window_title"))
        self._window.geometry("580x500")
        self._window.attributes("-topmost", True)
        self._window.resizable(True, True)
        self._window.minsize(450, 400)

        self._center_window()
        self._create_widgets()
        self._window.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _center_window(self) -> None:
        if self._window is None:
            return
        sw = self._window.winfo_screenwidth()
        sh = self._window.winfo_screenheight()
        x = (sw - 580) // 2
        y = (sh - 500) // 2
        self._window.geometry(f"580x500+{x}+{y}")

    def _create_widgets(self) -> None:
        if self._window is None:
            return

        main = ctk.CTkFrame(self._window, fg_color="#1e1e2e", corner_radius=0)
        main.pack(fill="both", expand=True)

        # 标题栏
        header = ctk.CTkFrame(main, fg_color="#181825", height=44, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ai_icon = self._icons.create_icon("ai", size=22, color="#cba6f7")
        ctk.CTkLabel(header, image=ai_icon, text="").pack(side="left", padx=(15, 8))

        ctk.CTkLabel(
            header,
            text=t("window_title"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#cba6f7"
        ).pack(side="left")

        close_icon = self._icons.create_icon("close", size=18, color="#f38ba8")
        ctk.CTkButton(
            header,
            image=close_icon,
            text="",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#313244",
            command=self._on_window_close,
            corner_radius=0
        ).pack(side="right")

        header.bind("<Button-1>", self._start_drag)
        header.bind("<B1-Motion>", self._on_drag)

        # 上下文信息栏
        ctx_frame = ctk.CTkFrame(main, fg_color="#313244", height=34, corner_radius=0)
        ctx_frame.pack(fill="x")
        ctx_frame.pack_propagate(False)

        source_icon = self._icons.create_icon("source", size=16, color="#a6adc8")
        self._app_label = ctk.CTkLabel(
            ctx_frame,
            image=source_icon,
            text=" Unknown",
            font=ctk.CTkFont(size=11),
            text_color="#a6adc8",
            compound="left"
        )
        self._app_label.pack(side="left", padx=15)

        ctk.CTkLabel(ctx_frame, text="|", text_color="#45475a", width=10).pack(side="left", padx=5)

        text_icon = self._icons.create_icon("text", size=16, color="#a6adc8")
        self._type_label = ctk.CTkLabel(
            ctx_frame,
            image=text_icon,
            text=" Analyzing...",
            font=ctk.CTkFont(size=11),
            text_color="#a6adc8",
            compound="left"
        )
        self._type_label.pack(side="left", padx=10)

        # 内容区域
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=10)

        # 原文区域
        orig_frame = ctk.CTkFrame(content, fg_color="#181825", corner_radius=8)
        orig_frame.pack(fill="x", pady=(0, 10))

        orig_header = ctk.CTkFrame(orig_frame, fg_color="transparent")
        orig_header.pack(fill="x", padx=12, pady=(10, 5))

        copy_icon = self._icons.create_icon("copy", size=16, color="#89b4fa")
        self._orig_header_label = ctk.CTkLabel(
            orig_header,
            image=copy_icon,
            text=f" {t('original')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#89b4fa",
            compound="left"
        )
        self._orig_header_label.pack(side="left")

        self._original_text = ctk.CTkTextbox(
            orig_frame,
            height=80,
            font=ctk.CTkFont(size=11, family="Consolas"),
            wrap="word",
            state="disabled",
            fg_color="#11111b",
            text_color="#cdd6f4",
            corner_radius=0,
            border_width=0
        )
        self._original_text.pack(fill="x", padx=12, pady=(0, 10))

        # AI结果区域
        result_frame = ctk.CTkFrame(content, fg_color="#181825", corner_radius=8)
        result_frame.pack(fill="both", expand=True, pady=(0, 10))

        result_header = ctk.CTkFrame(result_frame, fg_color="transparent")
        result_header.pack(fill="x", padx=12, pady=(10, 5))

        ai_small_icon = self._icons.create_icon("ai", size=16, color="#a6e3a1")
        self._result_header_label = ctk.CTkLabel(
            result_header,
            image=ai_small_icon,
            text=f" {t('ai_result')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#a6e3a1",
            compound="left"
        )
        self._result_header_label.pack(side="left")

        self._result_text = ctk.CTkTextbox(
            result_frame,
            font=ctk.CTkFont(size=12, family="Consolas"),
            wrap="word",
            state="disabled",
            fg_color="#11111b",
            text_color="#cdd6f4",
            corner_radius=0,
            border_width=0
        )
        self._result_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # 底部按钮
        footer = ctk.CTkFrame(main, fg_color="#181825", height=48, corner_radius=0)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        copy_result_icon = self._icons.create_icon("copy", size=16, color="#1e1e2e")
        self._copy_btn = ctk.CTkButton(
            footer,
            image=copy_result_icon,
            text=f" {t('copy_result')}",
            font=ctk.CTkFont(size=12),
            height=32,
            width=120,
            fg_color="#89b4fa",
            hover_color="#74c7ec",
            text_color="#1e1e2e",
            command=self._on_copy_click,
            corner_radius=6,
            compound="left"
        )
        self._copy_btn.pack(side="left", padx=(15, 8), pady=8)

        copy_orig_icon = self._icons.create_icon("copy", size=16, color="#cdd6f4")
        self._copy_orig_btn = ctk.CTkButton(
            footer,
            image=copy_orig_icon,
            text=f" {t('copy_original')}",
            font=ctk.CTkFont(size=12),
            height=32,
            width=130,
            fg_color="#585b70",
            hover_color="#45475a",
            command=self._on_copy_original_click,
            corner_radius=6,
            compound="left"
        )
        self._copy_orig_btn.pack(side="left", padx=8, pady=8)

        self._status_label = ctk.CTkLabel(
            footer,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#a6e3a1"
        )
        self._status_label.pack(side="left", padx=15, pady=8)

        close_btn_icon = self._icons.create_icon("close", size=14, color="#cdd6f4")
        self._close_btn = ctk.CTkButton(
            footer,
            image=close_btn_icon,
            text=f" {t('close')}",
            font=ctk.CTkFont(size=12),
            height=32,
            width=80,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self._on_window_close,
            corner_radius=6,
            compound="left"
        )
        self._close_btn.pack(side="right", padx=15, pady=8)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        if self._window:
            x = self._window.winfo_x() + (event.x - self._drag_x)
            y = self._window.winfo_y() + (event.y - self._drag_y)
            self._window.geometry(f"+{x}+{y}")

    def show(self, original_text: str, result_text: str, context_info: dict = None) -> None:
        if self._window is None:
            self._create_window()

        if context_info:
            self._update_context(context_info)

        self._set_text(self._original_text, original_text)
        self._set_text(self._result_text, result_text)

        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()
        self._is_visible = True
        self._set_status("")

    def _update_context(self, info: dict) -> None:
        app = info.get("app_name", "Unknown")
        cat = info.get("app_category", "other")
        ctype = info.get("content_type", "plain")
        lang = info.get("language", "")

        app_icon_name = self.APP_ICONS.get(cat, "source")
        app_icon = self._icons.create_icon(app_icon_name, size=16, color="#a6adc8")
        self._app_label.configure(image=app_icon, text=f" {app}")

        type_icon_name = self.TYPE_ICONS.get(ctype, "text")
        type_icon = self._icons.create_icon(type_icon_name, size=16, color="#a6adc8")
        type_names = {
            "error": t("cat_debug"),
            "code": t("cat_code"),
            "log": t("cat_log"),
            "config": t("cat_config"),
            "plain": t("cat_general")
        }
        type_text = type_names.get(ctype, "Unknown")
        if lang and lang != "unknown":
            type_text += f" ({lang})"
        self._type_label.configure(image=type_icon, text=f" {type_text}")

    def hide(self) -> None:
        if self._window:
            self._window.withdraw()
            self._is_visible = False

    def close(self) -> None:
        if self._window:
            self._window.destroy()
            self._window = None
            self._is_visible = False

    def _set_text(self, textbox, text):
        if textbox is None:
            return
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

    def _get_text(self, textbox) -> str:
        if textbox is None:
            return ""
        return textbox.get("1.0", "end-1c")

    def _set_status(self, msg):
        if self._status_label:
            self._status_label.configure(text=msg)

    def _on_copy_click(self):
        text = self._get_text(self._result_text)
        if text and self._on_copy:
            self._on_copy(text)
            self._set_status(t("copied"))
            if self._window:
                self._window.after(2000, lambda: self._set_status(""))

    def _on_copy_original_click(self):
        text = self._get_text(self._original_text)
        if text and self._on_copy:
            self._on_copy(text)
            self._set_status(t("original_copied"))
            if self._window:
                self._window.after(2000, lambda: self._set_status(""))

    def _on_window_close(self):
        self.hide()
        if self._on_close:
            self._on_close()

    def set_on_close(self, callback):
        self._on_close = callback

    def set_on_copy(self, callback):
        self._on_copy = callback

    def is_visible(self):
        return self._is_visible

    def update_result(self, text):
        if self._window:
            self._set_text(self._result_text, text)


_floating_window = None

def get_floating_window():
    global _floating_window
    if _floating_window is None:
        _floating_window = FloatingWindow()
    return _floating_window
