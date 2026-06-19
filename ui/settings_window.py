"""
设置窗口 - 支持多语言
"""

import threading
import customtkinter as ctk
from typing import Optional, Callable
from config import get_config
from ai_service import AIService
from language import t, get_lang_manager
from icons import get_icon_manager


class SettingsWindow:
    """设置窗口"""

    def __init__(self):
        self.config = get_config()
        self.lang_mgr = get_lang_manager()
        self._window: Optional[ctk.CTkToplevel] = None
        self._is_visible = False
        self._on_close: Optional[Callable] = None
        self._on_save: Optional[Callable] = None
        self._icons = get_icon_manager()
        self._entries = {}
        self._preset_var = None
        self._provider_var = None
        self._model_var = None
        self._lang_var = None

    def _create_window(self) -> None:
        if self._window is not None:
            return

        self._window = ctk.CTkToplevel()
        self._window.title(t("settings_title"))
        self._window.geometry("620x700")
        self._window.attributes("-topmost", True)
        self._window.resizable(False, False)

        self._center_window()
        self._create_widgets()
        self._load_config()
        self._window.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _center_window(self) -> None:
        if self._window is None:
            return
        sw = self._window.winfo_screenwidth()
        sh = self._window.winfo_screenheight()
        x = (sw - 620) // 2
        y = (sh - 700) // 2
        self._window.geometry(f"620x700+{x}+{y}")

    def _create_widgets(self) -> None:
        if self._window is None:
            return

        scroll_frame = ctk.CTkScrollableFrame(self._window)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== AI服务配置 =====
        ai_frame = ctk.CTkFrame(scroll_frame)
        ai_frame.pack(fill="x", pady=(0, 15))

        ai_header = ctk.CTkFrame(ai_frame, fg_color="transparent")
        ai_header.pack(fill="x", padx=15, pady=(15, 10))

        ai_icon = self._icons.create_icon("ai", size=20, color="#cba6f7")
        ctk.CTkLabel(
            ai_header,
            image=ai_icon,
            text=f" {t('settings_ai')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#cba6f7",
            compound="left"
        ).pack(side="left")

        # 预设服务
        self._create_preset_selector(ai_frame)

        # API Key
        self._create_label_entry(ai_frame, t("settings_api_key") + ":", "api_key", show="*")

        # Base URL
        self._create_label_entry(ai_frame, t("settings_base_url") + ":", "base_url")

        # Model
        model_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(model_frame, text=t("settings_model") + ":", width=100, anchor="w").pack(side="left")

        self._model_var = ctk.StringVar(value="gpt-4")
        self._model_menu = ctk.CTkOptionMenu(
            model_frame,
            variable=self._model_var,
            values=["gpt-4", "gpt-3.5-turbo"],
            width=220
        )
        self._model_menu.pack(side="left", padx=(10, 0))

        self._model_entry = ctk.CTkEntry(model_frame)
        self._model_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Provider
        provider_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        provider_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(provider_frame, text=t("settings_format") + ":", width=100, anchor="w").pack(side="left")

        self._provider_var = ctk.StringVar(value="openai_compatible")
        ctk.CTkOptionMenu(
            provider_frame,
            variable=self._provider_var,
            values=["openai_compatible", "claude"],
            width=220
        ).pack(side="left", padx=(10, 0))

        # 测试连接
        test_icon = self._icons.create_icon("test", size=16, color="#1e1e2e")
        ctk.CTkButton(
            ai_frame,
            image=test_icon,
            text=f" {t('settings_test')}",
            font=ctk.CTkFont(size=13),
            height=35,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._test_connection,
            compound="left"
        ).pack(padx=15, pady=(10, 15))

        # ===== 热键配置 =====
        hotkey_frame = ctk.CTkFrame(scroll_frame)
        hotkey_frame.pack(fill="x", pady=(0, 15))

        hotkey_header = ctk.CTkFrame(hotkey_frame, fg_color="transparent")
        hotkey_header.pack(fill="x", padx=15, pady=(15, 10))

        settings_icon = self._icons.create_icon("settings", size=20, color="#89b4fa")
        ctk.CTkLabel(
            hotkey_header,
            image=settings_icon,
            text=f" {t('settings_hotkey')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#89b4fa",
            compound="left"
        ).pack(side="left")

        self._create_label_entry(hotkey_frame, t("hotkey_key") + ":", "hotkey")

        ctk.CTkLabel(
            hotkey_frame,
            text="Format: ctrl+shift+q, alt+a, f2",
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af"
        ).pack(fill="x", padx=15, pady=(0, 15))

        # ===== 语言设置 =====
        lang_frame = ctk.CTkFrame(scroll_frame)
        lang_frame.pack(fill="x", pady=(0, 15))

        lang_header = ctk.CTkFrame(lang_frame, fg_color="transparent")
        lang_header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            lang_header,
            text=f" {t('settings_language')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f9e2af"
        ).pack(side="left")

        lang_select_frame = ctk.CTkFrame(lang_frame, fg_color="transparent")
        lang_select_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(lang_select_frame, text=t("settings_language") + ":", width=100, anchor="w").pack(side="left")

        self._lang_var = ctk.StringVar(value=self.lang_mgr.get_lang())
        langs = self.lang_mgr.get_available_langs()
        lang_names = [self.lang_mgr.get_lang_name(l) for l in langs]

        ctk.CTkOptionMenu(
            lang_select_frame,
            variable=self._lang_var,
            values=lang_names,
            width=220,
            command=self._on_lang_change
        ).pack(side="left", padx=(10, 0))

        # ===== 自定义提示词 =====
        prompt_frame = ctk.CTkFrame(scroll_frame)
        prompt_frame.pack(fill="x", pady=(0, 15))

        prompt_header = ctk.CTkFrame(prompt_frame, fg_color="transparent")
        prompt_header.pack(fill="x", padx=15, pady=(15, 10))

        text_icon = self._icons.create_icon("text", size=20, color="#a6e3a1")
        ctk.CTkLabel(
            prompt_header,
            image=text_icon,
            text=f" {t('settings_prompt')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#a6e3a1",
            compound="left"
        ).pack(side="left")

        ctk.CTkLabel(
            prompt_frame,
            text=t("settings_prompt_desc"),
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af",
            wraplength=550
        ).pack(fill="x", padx=15, pady=(0, 10))

        self._prompt_text = ctk.CTkTextbox(
            prompt_frame,
            height=80,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self._prompt_text.pack(fill="x", padx=15, pady=(0, 15))

        # ===== 按钮栏 =====
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        save_icon = self._icons.create_icon("save", size=16, color="#1e1e2e")
        ctk.CTkButton(
            button_frame,
            image=save_icon,
            text=f" {t('save')}",
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self._save_config,
            compound="left"
        ).pack(side="left", padx=(0, 10))

        reset_icon = self._icons.create_icon("reset", size=16, color="#cdd6f4")
        ctk.CTkButton(
            button_frame,
            image=reset_icon,
            text=f" {t('reset')}",
            font=ctk.CTkFont(size=14),
            height=40,
            width=100,
            fg_color="#585b70",
            hover_color="#45475a",
            command=self._reset_config,
            compound="left"
        ).pack(side="left")

        self._status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#a6e3a1"
        )
        self._status_label.pack(side="right")

    def _create_preset_selector(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(frame, text=t("settings_preset") + ":", width=100, anchor="w").pack(side="left")

        preset_services = AIService.get_preset_services()
        preset_names = [t("settings_custom")] + [s["name"] for s in preset_services.values()]
        preset_ids = ["custom"] + list(preset_services.keys())

        self._preset_var = ctk.StringVar(value="custom")
        ctk.CTkOptionMenu(
            frame,
            variable=self._preset_var,
            values=preset_names,
            width=220,
            command=lambda choice: self._on_preset_change(choice, preset_ids, preset_names)
        ).pack(side="left", padx=(10, 0))

    def _create_label_entry(self, parent, label_text: str, key: str, show: str = None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(frame, text=label_text, width=100, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(frame, show=show)
        entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        self._entries[key] = entry

    def _on_preset_change(self, choice: str, preset_ids: list, preset_names: list):
        try:
            index = preset_names.index(choice)
            preset_id = preset_ids[index]
        except ValueError:
            return

        if preset_id == "custom":
            return

        preset = AIService.get_preset_service(preset_id)
        if preset:
            if "base_url" in self._entries:
                self._entries["base_url"].delete(0, "end")
                self._entries["base_url"].insert(0, preset["base_url"])

            if "models" in preset:
                self._model_menu.configure(values=preset["models"])
                self._model_var.set(preset["models"][0])

            if "provider" in preset:
                self._provider_var.set(preset["provider"])

    def _on_lang_change(self, choice: str):
        """语言切换"""
        langs = self.lang_mgr.get_available_langs()
        lang_names = [self.lang_mgr.get_lang_name(l) for l in langs]

        try:
            index = lang_names.index(choice)
            lang_code = langs[index]
            self.lang_mgr.set_lang(lang_code)
        except:
            pass

    def _load_config(self):
        if "api_key" in self._entries:
            self._entries["api_key"].insert(0, self.config.get("ai_service.api_key", ""))
        if "base_url" in self._entries:
            self._entries["base_url"].insert(0, self.config.get("ai_service.base_url", ""))

        model = self.config.get("ai_service.model", "gpt-4")
        self._model_var.set(model)
        self._provider_var.set(self.config.get("ai_service.provider", "openai_compatible"))

        if "hotkey" in self._entries:
            self._entries["hotkey"].insert(0, self.config.get("hotkey.trigger", "ctrl+shift+q"))

        # 语言
        self._lang_var.set(self.lang_mgr.get_lang_name(self.lang_mgr.get_lang()))

    def _save_config(self):
        if "api_key" in self._entries:
            self.config.set("ai_service.api_key", self._entries["api_key"].get())
        if "base_url" in self._entries:
            self.config.set("ai_service.base_url", self._entries["base_url"].get())

        model = self._model_var.get()
        custom_model = self._model_entry.get().strip() if self._model_entry else ""
        if custom_model:
            model = custom_model
        self.config.set("ai_service.model", model)
        self.config.set("ai_service.provider", self._provider_var.get())

        if "hotkey" in self._entries:
            self.config.set("hotkey.trigger", self._entries["hotkey"].get())

        # 保存语言
        langs = self.lang_mgr.get_available_langs()
        lang_names = [self.lang_mgr.get_lang_name(l) for l in langs]
        try:
            index = lang_names.index(self._lang_var.get())
            self.config.set("general.language", langs[index])
        except:
            pass

        if self.config.save():
            self._set_status(t("settings_saved"))
            if self._on_save:
                self._on_save()
        else:
            self._set_status(t("settings_save_failed"))

    def _reset_config(self):
        self.config.reset_to_default()
        self._load_config()
        self._set_status(t("reset"))

    def _test_connection(self):
        self._save_config()

        from ai_service import reload_ai_service
        ai_service = reload_ai_service()

        self._set_status(t("settings_testing"))

        def test():
            result = ai_service.test_connection()
            if self._window:
                self._window.after(0, lambda: self._set_status(
                    t("settings_connected") if result["success"] else f"{t('settings_connect_failed')}: {result['message'][:30]}"
                ))

        threading.Thread(target=test, daemon=True).start()

    def _set_status(self, message: str):
        if self._status_label:
            if t("settings_connected") in message or t("settings_saved") in message:
                color = "#a6e3a1"
            elif t("settings_connect_failed") in message or t("settings_save_failed") in message:
                color = "#f38ba8"
            else:
                color = "#a6adc8"
            self._status_label.configure(text=message, text_color=color)

    def _on_window_close(self):
        self.close()
        if self._on_close:
            self._on_close()

    def show(self):
        if self._window is None:
            self._create_window()
        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()
        self._is_visible = True

    def close(self):
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
