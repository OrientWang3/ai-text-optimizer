"""
AI文本优化器 - 主程序
支持多语言
"""

import sys
import threading
import pyperclip
import customtkinter as ctk
from config import get_config
from ai_service import get_ai_service, reload_ai_service, AIServiceError
from prompt_templates import get_template_manager
from clipboard import get_text_selector
from context_analyzer import get_context_analyzer
from hotkey import get_hotkey_listener, stop_hotkey_listener
from language import t, get_lang_manager
from ui import (
    get_floating_window, SettingsWindow, get_tray_icon, stop_tray_icon,
    get_hotkey_window, get_template_window
)


class AITextOptimizer:
    """AI文本优化器"""

    def __init__(self):
        self.config = get_config()
        self.ai_service = get_ai_service()
        self.text_selector = get_text_selector()
        self.context_analyzer = get_context_analyzer()
        self.template_mgr = get_template_manager()
        self.lang_mgr = get_lang_manager()

        self.settings_window = None
        self.hotkey_window = None
        self.template_window = None

        self._current_template = "code_fix"
        self._enable_logging = self.config.get("general.enable_logging", False)

        self.root = ctk.CTk()
        self.root.withdraw()

        self.floating_window = get_floating_window()
        self.tray_icon = get_tray_icon()

        self._setup_callbacks()
        self.hotkey_listener = None
        self._processing = False

    def _log(self, msg: str):
        if self._enable_logging:
            print(msg)

    def _setup_callbacks(self):
        self.floating_window.set_on_copy(self._copy_to_clipboard)
        self.tray_icon.set_on_settings(self._show_settings)
        self.tray_icon.set_on_hotkey_settings(self._show_hotkey_settings)
        self.tray_icon.set_on_templates(self._show_templates)
        self.tray_icon.set_on_quit(self._quit)
        self.tray_icon.set_on_toggle_hotkey(self._toggle_hotkey)
        self.tray_icon.set_on_change_lang(self._on_language_change)

    def _copy_to_clipboard(self, text: str):
        pyperclip.copy(text)

    def _show_settings(self):
        self.root.after(0, self._show_settings_thread)

    def _show_settings_thread(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
            self.settings_window.set_on_close(lambda: setattr(self, 'settings_window', None))
            self.settings_window.set_on_save(self._on_settings_save)
        self.settings_window.show()

    def _show_hotkey_settings(self):
        self.root.after(0, self._show_hotkey_thread)

    def _show_hotkey_thread(self):
        if self.hotkey_window is None:
            self.hotkey_window = get_hotkey_window()
            self.hotkey_window.set_on_close(lambda: setattr(self, 'hotkey_window', None))
            self.hotkey_window.set_on_save(self._on_hotkey_save)
        self.hotkey_window.show()

    def _show_templates(self):
        self.root.after(0, self._show_templates_thread)

    def _show_templates_thread(self):
        if self.template_window is None:
            self.template_window = get_template_window()
            self.template_window.set_on_close(lambda: setattr(self, 'template_window', None))
            self.template_window.set_on_select(self._on_template_select)
        self.template_window.show()

    def _on_template_select(self, template_key: str):
        self._current_template = template_key
        template = self.template_mgr.get_template(template_key)
        if template:
            print(f"[Template] {template.name}")

    def _on_hotkey_save(self, new_hotkey: str):
        print(f"[Hotkey] {new_hotkey}")
        if self.hotkey_listener:
            self.hotkey_listener.update_hotkey(new_hotkey)
        self.tray_icon.update_hotkey_display()
        self.config = get_config()

    def _on_settings_save(self):
        self.config = get_config()
        self.ai_service = reload_ai_service()
        self._enable_logging = self.config.get("general.enable_logging", False)
        if self.hotkey_listener:
            self.hotkey_listener.update_hotkey(self.config.get_hotkey())

    def _on_language_change(self, lang: str):
        """语言切换回调"""
        print(f"[Lang] {lang}")
        self.tray_icon.update_language()

    def _toggle_hotkey(self, enabled: bool):
        if self.hotkey_listener:
            if enabled:
                self.hotkey_listener.start()
            else:
                self.hotkey_listener.stop()
            self.tray_icon.set_hotkey_enabled(enabled)

    def _on_hotkey_triggered(self):
        if self._processing:
            return

        print(f"\n[Hotkey] Triggered")

        try:
            text = pyperclip.paste()
        except:
            text = ""

        if text and text.strip():
            print(f"[Hotkey] Got text: {len(text)} chars")
            self.root.after(0, self._process_text, text)
        else:
            print("[Hotkey] Empty")
            self.root.after(0, self._show_no_text)

    def _show_no_text(self):
        self.floating_window.show(
            t("no_text"),
            t("no_text_msg"),
            {"app_name": "System", "app_category": "other", "content_type": "plain", "language": ""}
        )

    def _process_text(self, text: str):
        self._log("[Process] Start")
        self._processing = True

        context = self.context_analyzer.get_active_window()
        analysis = self.context_analyzer.analyze_text(text, context)

        print(f"[Process] App: {context.app_name}")
        print(f"[Process] Type: {analysis.content_type}")

        context_info = {
            "app_name": context.app_name,
            "app_category": context.category,
            "content_type": analysis.content_type,
            "language": analysis.language,
        }
        self.floating_window.show(text, t("analyzing"), context_info)

        threading.Thread(target=self._call_ai, args=(text, context, analysis), daemon=True).start()

    def _call_ai(self, text: str, context, analysis):
        self._log("[AI] Calling...")
        try:
            source = f"{context.app_name} ({context.category})"
            language = analysis.language if analysis.language != "unknown" else ""

            prompt = self.template_mgr.format_prompt(
                self._current_template,
                text,
                source=source,
                language=language
            )

            if not prompt:
                result = self.ai_service.analyze_and_optimize(text)
            else:
                messages = [
                    {"role": "system", "content": "你是一个专业的技术助手。请用纯文本回答，不要使用Markdown格式。不要重复用户发送的原文内容，只输出你的分析和建议。"},
                    {"role": "user", "content": prompt}
                ]
                response = self.ai_service.chat(messages)

                from text_cleaner import clean_markdown
                response = clean_markdown(response)

                result = {
                    "context": context,
                    "analysis": analysis,
                    "response": response
                }

            print("[AI] Done")
            self.root.after(0, self._update_result, result)

        except AIServiceError as e:
            error_msg = f"{t('ai_error')}: {str(e)}"
            print(f"[AI] {error_msg}")
            self.root.after(0, self._update_error, error_msg)
        except Exception as e:
            error_msg = f"{t('error')}: {str(e)}"
            print(f"[AI] {error_msg}")
            import traceback
            traceback.print_exc()
            self.root.after(0, self._update_error, error_msg)
        finally:
            self._processing = False

    def _update_result(self, result: dict):
        response = result.get("response", "No response")
        self.floating_window.update_result(response)

    def _update_error(self, error_msg: str):
        self.floating_window.update_result(error_msg)

    def _quit(self):
        print("[Quit]")
        stop_hotkey_listener()
        stop_tray_icon()
        if self.settings_window:
            self.settings_window.close()
        if self.hotkey_window:
            self.hotkey_window.close()
        if self.template_window:
            self.template_window.close()
        self.floating_window.close()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        hotkey = self.config.get_hotkey()
        template = self.template_mgr.get_template(self._current_template)
        template_name = template.name if template else "Default"

        print("\n" + "="*50)
        print(f"   {t('start_title')}")
        print("="*50)
        print(f"\n   {t('start_hotkey')}: {hotkey.upper().replace('+', ' + ')}")
        print(f"   {t('start_template')}: {template_name}")
        print(f"\n   {t('start_usage')}:")
        print(f"   {t('start_step1')}")
        print(f"   {t('start_step2')}")
        print(f"   {t('start_step3')}")
        print(f"   {t('start_step4')}")
        print(f"\n   {t('start_change')}:")
        print(f"   {t('start_change_tip')}")
        print("\n" + "="*50)

        self.tray_icon.start()

        self.hotkey_listener = get_hotkey_listener(self._on_hotkey_triggered)
        self.hotkey_listener.start()

        print(f"[{t('start_ready')}]\n")

        self.root.mainloop()


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = AITextOptimizer()
    app.run()


if __name__ == "__main__":
    main()
