"""
提示词模板选择窗口 - 支持多语言，支持添加
"""

import customtkinter as ctk
from typing import Optional, Callable
from prompt_templates import get_template_manager, PromptTemplate
from language import t
from icons import get_icon_manager


class TemplateWindow:
    """模板选择窗口"""

    def __init__(self):
        self._window: Optional[ctk.CTkToplevel] = None
        self._is_visible = False
        self._on_close: Optional[Callable] = None
        self._on_select: Optional[Callable[[str], None]] = None
        self._icons = get_icon_manager()
        self._template_mgr = get_template_manager()

        self._template_list = None
        self._preview_text = None
        self._current_key = None

        self._edit_btn = None
        self._delete_btn = None
        self._select_btn = None
        self._selected_label = None

        self._edit_window = None

    def _create_window(self) -> None:
        if self._window is not None:
            return

        self._window = ctk.CTkToplevel()
        self._window.title(t("template_title"))
        self._window.geometry("700x550")
        self._window.attributes("-topmost", True)
        self._window.resizable(True, True)
        self._window.minsize(600, 450)

        self._center_window()
        self._create_widgets()
        self._load_templates()
        self._window.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _center_window(self) -> None:
        if self._window is None:
            return
        sw = self._window.winfo_screenwidth()
        sh = self._window.winfo_screenheight()
        x = (sw - 700) // 2
        y = (sh - 550) // 2
        self._window.geometry(f"700x550+{x}+{y}")

    def _create_widgets(self) -> None:
        if self._window is None:
            return

        main = ctk.CTkFrame(self._window, fg_color="#1e1e2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题栏
        header = ctk.CTkFrame(main, fg_color="#181825", height=45)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=t("template_title"),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#cba6f7"
        ).pack(side="left", padx=15)

        # 添加按钮
        ctk.CTkButton(
            header,
            text=f"+ {t('add')}",
            font=ctk.CTkFont(size=12),
            height=30,
            width=80,
            fg_color="#a6e3a1",
            hover_color="#94e2d5",
            text_color="#1e1e2e",
            command=self._on_add_click,
            corner_radius=6
        ).pack(side="right", padx=15)

        # 内容区域
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # 左侧：模板列表
        left_frame = ctk.CTkFrame(content, fg_color="#181825", width=250, corner_radius=8)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(
            left_frame,
            text=t("template_list"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#89b4fa"
        ).pack(padx=15, pady=(10, 5))

        self._template_list = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self._template_list.pack(fill="both", expand=True, padx=5, pady=5)

        # 右侧：预览
        right_frame = ctk.CTkFrame(content, fg_color="#181825", corner_radius=8)
        right_frame.pack(side="right", fill="both", expand=True)

        preview_header = ctk.CTkFrame(right_frame, fg_color="transparent")
        preview_header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            preview_header,
            text=t("template_preview"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a6e3a1"
        ).pack(side="left")

        # 操作按钮
        btn_frame = ctk.CTkFrame(preview_header, fg_color="transparent")
        btn_frame.pack(side="right")

        self._edit_btn = ctk.CTkButton(
            btn_frame,
            text=t("edit"),
            font=ctk.CTkFont(size=11),
            height=25,
            width=60,
            fg_color="#585b70",
            hover_color="#45475a",
            command=self._on_edit_click,
            corner_radius=4,
            state="disabled"
        )
        self._edit_btn.pack(side="left", padx=2)

        self._delete_btn = ctk.CTkButton(
            btn_frame,
            text=t("delete"),
            font=ctk.CTkFont(size=11),
            height=25,
            width=60,
            fg_color="#f38ba8",
            hover_color="#eba0ac",
            text_color="#1e1e2e",
            command=self._on_delete_click,
            corner_radius=4,
            state="disabled"
        )
        self._delete_btn.pack(side="left", padx=2)

        # 预览文本
        self._preview_text = ctk.CTkTextbox(
            right_frame,
            font=ctk.CTkFont(size=12, family="Consolas"),
            wrap="word",
            state="disabled",
            fg_color="#11111b",
            text_color="#cdd6f4"
        )
        self._preview_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # 底部按钮
        footer = ctk.CTkFrame(main, fg_color="transparent", height=40)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        footer.pack_propagate(False)

        self._select_btn = ctk.CTkButton(
            footer,
            text=t("template_use"),
            font=ctk.CTkFont(size=13),
            height=35,
            width=120,
            fg_color="#89b4fa",
            hover_color="#74c7ec",
            text_color="#1e1e2e",
            command=self._on_use_click,
            corner_radius=6,
            state="disabled"
        )
        self._select_btn.pack(side="left")

        ctk.CTkButton(
            footer,
            text=t("close"),
            font=ctk.CTkFont(size=13),
            height=35,
            width=80,
            fg_color="#585b70",
            hover_color="#45475a",
            command=self._on_window_close,
            corner_radius=6
        ).pack(side="right")

        self._selected_label = ctk.CTkLabel(
            footer,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#a6adc8"
        )
        self._selected_label.pack(side="left", padx=15)

    def _load_templates(self):
        """加载模板列表"""
        if self._template_list is None:
            return

        for widget in self._template_list.winfo_children():
            widget.destroy()

        templates = self._template_mgr.get_all_templates()

        # 按分类分组
        categories = {}
        for key, template in templates.items():
            cat = template.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, template))

        # 分类名称
        cat_names = {
            "code": t("cat_code"),
            "debug": t("cat_debug"),
            "config": t("cat_config"),
            "log": t("cat_log"),
            "general": t("cat_general"),
            "custom": t("cat_custom")
        }

        for cat, items in categories.items():
            cat_display = cat_names.get(cat, cat.upper())
            cat_label = ctk.CTkLabel(
                self._template_list,
                text=f"[{cat_display}]",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#f9e2af",
                anchor="w"
            )
            cat_label.pack(fill="x", padx=5, pady=(8, 2))

            for key, template in items:
                self._create_template_item(key, template)

    def _create_template_item(self, key: str, template: PromptTemplate):
        """创建模板列表项"""
        item_frame = ctk.CTkFrame(
            self._template_list,
            fg_color="#313244",
            corner_radius=6,
            height=35
        )
        item_frame.pack(fill="x", padx=5, pady=2)
        item_frame.pack_propagate(False)

        display_name = template.get_display_name()

        name_label = ctk.CTkLabel(
            item_frame,
            text=display_name,
            font=ctk.CTkFont(size=12),
            text_color="#cdd6f4",
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=10)

        def on_click(e=None, k=key, t=template):
            self._select_template(k, t)

        item_frame.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)

        def on_enter(e=None):
            item_frame.configure(fg_color="#45475a")

        def on_leave(e=None):
            if self._current_key != key:
                item_frame.configure(fg_color="#313244")

        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)

    def _select_template(self, key: str, template: PromptTemplate):
        """选择模板"""
        self._current_key = key

        if self._preview_text:
            self._preview_text.configure(state="normal")
            self._preview_text.delete("1.0", "end")
            self._preview_text.insert("1.0", template.prompt)
            self._preview_text.configure(state="disabled")

        self._edit_btn.configure(state="normal")
        self._select_btn.configure(state="normal")

        if key in self._template_mgr.BUILTIN_TEMPLATES:
            self._delete_btn.configure(state="disabled")
        else:
            self._delete_btn.configure(state="normal")

        display_name = template.get_display_name()
        self._selected_label.configure(text=f"{t('template_selected')}: {display_name}")

    def _on_use_click(self):
        """使用模板"""
        if self._current_key and self._on_select:
            self._on_select(self._current_key)
        self.close()

    def _on_add_click(self):
        """添加按钮点击"""
        print("[Template] Add clicked")
        self._show_edit_dialog(None)

    def _on_edit_click(self):
        """编辑按钮点击"""
        if self._current_key:
            print(f"[Template] Edit clicked: {self._current_key}")
            self._show_edit_dialog(self._current_key)

    def _on_delete_click(self):
        """删除按钮点击"""
        if self._current_key:
            print(f"[Template] Delete clicked: {self._current_key}")
            self._template_mgr.delete_template(self._current_key)
            self._current_key = None
            self._load_templates()

            if self._preview_text:
                self._preview_text.configure(state="normal")
                self._preview_text.delete("1.0", "end")
                self._preview_text.configure(state="disabled")

            self._edit_btn.configure(state="disabled")
            self._delete_btn.configure(state="disabled")
            self._select_btn.configure(state="disabled")
            self._selected_label.configure(text="")

    def _show_edit_dialog(self, key: Optional[str]):
        """显示编辑对话框"""
        print(f"[Template] _show_edit_dialog, key={key}")

        # 关闭已有的编辑窗口
        if self._edit_window is not None:
            print("[Template] Closing existing edit window")
            self._edit_window.destroy()
            self._edit_window = None

        is_edit = key is not None
        template = self._template_mgr.get_template(key) if is_edit else None

        # 创建新窗口
        print("[Template] Creating new edit window")
        self._edit_window = ctk.CTkToplevel()
        self._edit_window.title(t("template_edit") if is_edit else t("template_add"))
        self._edit_window.geometry("600x600")
        self._edit_window.attributes("-topmost", True)
        self._edit_window.resizable(True, True)
        self._edit_window.minsize(500, 500)

        # 设置关闭协议
        self._edit_window.protocol("WM_DELETE_WINDOW", self._close_edit_window)

        # 居中
        sw = self._edit_window.winfo_screenwidth()
        sh = self._edit_window.winfo_screenheight()
        x = (sw - 550) // 2
        y = (sh - 500) // 2
        self._edit_window.geometry(f"550x500+{x}+{y}")

        # 主框架
        main = ctk.CTkFrame(self._edit_window, fg_color="#1e1e2e")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # 标题
        title_text = t("template_edit") if is_edit else t("template_add")
        ctk.CTkLabel(
            main,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#cba6f7"
        ).pack(pady=(0, 15))

        # Key (仅新建时)
        key_entry = None
        if not is_edit:
            key_frame = ctk.CTkFrame(main, fg_color="transparent")
            key_frame.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(key_frame, text=t("template_key") + ":", width=100, anchor="w").pack(side="left")
            key_entry = ctk.CTkEntry(key_frame, placeholder_text="my_template")
            key_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Name
        name_frame = ctk.CTkFrame(main, fg_color="transparent")
        name_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(name_frame, text=t("template_name") + ":", width=100, anchor="w").pack(side="left")
        name_entry = ctk.CTkEntry(name_frame)
        name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        if template:
            name_entry.insert(0, template.name)

        # Description
        desc_frame = ctk.CTkFrame(main, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(desc_frame, text=t("template_desc") + ":", width=100, anchor="w").pack(side="left")
        desc_entry = ctk.CTkEntry(desc_frame)
        desc_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        if template:
            desc_entry.insert(0, template.description)

        # Category
        cat_frame = ctk.CTkFrame(main, fg_color="transparent")
        cat_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(cat_frame, text=t("template_category") + ":", width=100, anchor="w").pack(side="left")
        cat_var = ctk.StringVar(value=template.category if template else "custom")
        ctk.CTkOptionMenu(
            cat_frame,
            variable=cat_var,
            values=["code", "debug", "config", "log", "general", "custom"],
            width=150
        ).pack(side="left", padx=(10, 0))

        # Prompt
        ctk.CTkLabel(main, text=t("template_prompt") + ":", anchor="w").pack(fill="x", pady=(5, 5))

        prompt_text = ctk.CTkTextbox(
            main,
            font=ctk.CTkFont(size=12, family="Consolas"),
            wrap="word",
            fg_color="#11111b",
            text_color="#cdd6f4"
        )
        prompt_text.pack(fill="both", expand=True, pady=(0, 10))

        if template:
            prompt_text.insert("1.0", template.prompt)
        else:
            prompt_text.insert("1.0", """You are an expert. Analyze the following:

IMPORTANT: Reply in plain text only. Do NOT use Markdown.

Source: {source}
Content:
{text}

Please provide your analysis.""")

        # 状态标签
        status_label = ctk.CTkLabel(main, text="", font=ctk.CTkFont(size=11), text_color="#f38ba8")
        status_label.pack(pady=(0, 5))

        # 按钮框架
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        def save():
            """保存模板"""
            new_key = key_entry.get().strip() if key_entry else key
            new_name = name_entry.get().strip()
            new_desc = desc_entry.get().strip()
            new_prompt = prompt_text.get("1.0", "end-1c").strip()
            new_cat = cat_var.get()

            # 验证
            if not is_edit and not new_key:
                status_label.configure(text=f"Please enter {t('template_key')}")
                return

            if not new_name:
                status_label.configure(text=f"Please enter {t('template_name')}")
                return

            if not new_prompt:
                status_label.configure(text=f"Please enter {t('template_prompt')}")
                return

            # 保存
            if is_edit:
                success = self._template_mgr.update_template(
                    key,
                    name=new_name,
                    description=new_desc,
                    prompt=new_prompt
                )
            else:
                success = self._template_mgr.add_template(
                    new_key,
                    name=new_name,
                    description=new_desc,
                    prompt=new_prompt,
                    category=new_cat
                )

            if success:
                print(f"[Template] Saved: {new_key}")
                self._load_templates()
                self._edit_window.destroy()
                self._edit_window = None
            else:
                status_label.configure(text="Failed to save (key may already exist)")

        # 保存按钮
        ctk.CTkButton(
            btn_frame,
            text=t("save"),
            font=ctk.CTkFont(size=13),
            height=35,
            width=100,
            fg_color="#a6e3a1",
            hover_color="#94e2d5",
            text_color="#1e1e2e",
            command=save,
            corner_radius=6
        ).pack(side="left")

        # 取消按钮
        ctk.CTkButton(
            btn_frame,
            text=t("cancel"),
            font=ctk.CTkFont(size=13),
            height=35,
            width=80,
            fg_color="#585b70",
            hover_color="#45475a",
            command=self._close_edit_window,
            corner_radius=6
        ).pack(side="left", padx=10)

        # 强制显示窗口
        print("[Template] Updating window")
        self._edit_window.update_idletasks()

        # 重新计算位置（使用主窗口位置）
        if self._window:
            main_x = self._window.winfo_x()
            main_y = self._window.winfo_y()
            # 在主窗口旁边显示
            new_x = main_x + 50
            new_y = main_y + 50
            self._edit_window.geometry(f"600x600+{new_x}+{new_y}")
            print(f"[Template] Position: {new_x}, {new_y}")

        print("[Template] Showing window")
        self._edit_window.deiconify()
        self._edit_window.lift()
        self._edit_window.focus_force()

        print("[Template] Edit dialog shown successfully")

    def _close_edit_window(self):
        """关闭编辑窗口"""
        if self._edit_window:
            self._edit_window.destroy()
            self._edit_window = None

    def _on_window_close(self):
        """关闭主窗口"""
        self._close_edit_window()
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
        self._close_edit_window()
        if self._window:
            self._window.destroy()
            self._window = None
            self._is_visible = False

    def set_on_close(self, callback):
        self._on_close = callback

    def set_on_select(self, callback):
        self._on_select = callback

    def is_visible(self):
        return self._is_visible


_template_window = None

def get_template_window():
    global _template_window
    if _template_window is None:
        _template_window = TemplateWindow()
    return _template_window
