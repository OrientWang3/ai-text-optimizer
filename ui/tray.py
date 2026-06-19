"""
系统托盘模块 - 支持多语言
"""

import threading
from typing import Optional, Callable
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from config import get_config
from language import t, get_lang_manager


class TrayIcon:
    """系统托盘图标"""

    def __init__(self):
        self.config = get_config()
        self.lang_mgr = get_lang_manager()
        self._icon: Optional[pystray.Icon] = None
        self._is_running = False

        self._on_settings: Optional[Callable] = None
        self._on_hotkey_settings: Optional[Callable] = None
        self._on_templates: Optional[Callable] = None
        self._on_quit: Optional[Callable] = None
        self._on_toggle_hotkey: Optional[Callable] = None
        self._on_change_lang: Optional[Callable] = None

        self._hotkey_enabled = True

    def _create_icon_image(self) -> Image.Image:
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, width-4, height-4], fill='#89b4fa')
        draw.text((width//2, height//2), "AI", fill='#1e1e2e', anchor='mm')
        return image

    def _create_menu(self) -> pystray.Menu:
        hotkey = self.config.get_hotkey().upper().replace("+", "+")
        lang = self.lang_mgr.get_lang()
        lang_name = self.lang_mgr.get_lang_name(lang)

        return pystray.Menu(
            item(
                f'{t("tray_hotkey")}: {hotkey}',
                self._on_hotkey_settings_click,
                default=True
            ),
            item(
                t("tray_hotkey_on") if self._hotkey_enabled else t("tray_hotkey_off"),
                self._on_toggle_hotkey_click
            ),
            pystray.Menu.SEPARATOR,
            item(
                t("tray_templates"),
                self._on_templates_click
            ),
            item(
                t("tray_settings"),
                self._on_settings_click
            ),
            item(
                f'{t("settings_language")}: {lang_name}',
                self._on_lang_submenu
            ),
            pystray.Menu.SEPARATOR,
            item(
                t("tray_quit"),
                self._on_quit_click
            )
        )

    def _on_lang_submenu(self, icon, item):
        """语言子菜单"""
        current_lang = self.lang_mgr.get_lang()

        def create_lang_menu():
            langs = self.lang_mgr.get_available_langs()
            items = []
            for lang in langs:
                name = self.lang_mgr.get_lang_name(lang)
                is_current = lang == current_lang
                items.append(
                    item(
                        f"{'✓ ' if is_current else ''}{name}",
                        lambda e, i, l=lang: self._change_language(l)
                    )
                )
            return pystray.Menu(*items)

        # 显示子菜单
        icon.menu = create_lang_menu()

    def _change_language(self, lang: str):
        """切换语言"""
        self.lang_mgr.set_lang(lang)

        # 保存到配置
        self.config.set("general.language", lang)
        self.config.save()

        # 更新菜单
        if self._icon:
            self._icon.menu = self._create_menu()

        # 通知回调
        if self._on_change_lang:
            self._on_change_lang(lang)

    def _on_settings_click(self, icon, item) -> None:
        if self._on_settings:
            self._on_settings()

    def _on_hotkey_settings_click(self, icon, item) -> None:
        if self._on_hotkey_settings:
            self._on_hotkey_settings()

    def _on_templates_click(self, icon, item) -> None:
        if self._on_templates:
            self._on_templates()

    def _on_toggle_hotkey_click(self, icon, item) -> None:
        self._hotkey_enabled = not self._hotkey_enabled
        icon.menu = self._create_menu()
        if self._on_toggle_hotkey:
            self._on_toggle_hotkey(self._hotkey_enabled)

    def _on_quit_click(self, icon, item) -> None:
        self.stop()
        if self._on_quit:
            self._on_quit()

    def _run(self) -> None:
        self._icon = pystray.Icon(
            t("app_name"),
            self._create_icon_image(),
            t("app_name"),
            self._create_menu()
        )
        self._icon.run()

    def start(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._is_running:
            return
        self._is_running = False
        if self._icon:
            self._icon.stop()
            self._icon = None

    def update_tooltip(self, text: str) -> None:
        if self._icon:
            self._icon.title = text

    def update_hotkey_display(self):
        if self._icon:
            self._icon.menu = self._create_menu()

    def update_language(self):
        """更新语言显示"""
        if self._icon:
            self._icon.menu = self._create_menu()

    def set_hotkey_enabled(self, enabled: bool) -> None:
        self._hotkey_enabled = enabled
        if self._icon:
            self._icon.menu = self._create_menu()

    def set_on_settings(self, callback: Callable) -> None:
        self._on_settings = callback

    def set_on_hotkey_settings(self, callback: Callable) -> None:
        self._on_hotkey_settings = callback

    def set_on_templates(self, callback: Callable) -> None:
        self._on_templates = callback

    def set_on_quit(self, callback: Callable) -> None:
        self._on_quit = callback

    def set_on_toggle_hotkey(self, callback: Callable) -> None:
        self._on_toggle_hotkey = callback

    def set_on_change_lang(self, callback: Callable) -> None:
        self._on_change_lang = callback

    def is_running(self) -> bool:
        return self._is_running


_tray_icon = None

def get_tray_icon() -> TrayIcon:
    global _tray_icon
    if _tray_icon is None:
        _tray_icon = TrayIcon()
    return _tray_icon

def stop_tray_icon() -> None:
    global _tray_icon
    if _tray_icon:
        _tray_icon.stop()
        _tray_icon = None
