"""
UI模块
"""

from .floating_window import FloatingWindow, get_floating_window
from .settings_window import SettingsWindow
from .tray import TrayIcon, get_tray_icon, stop_tray_icon
from .hotkey_window import HotkeyWindow, get_hotkey_window
from .template_window import TemplateWindow, get_template_window

__all__ = [
    'FloatingWindow',
    'get_floating_window',
    'SettingsWindow',
    'TrayIcon',
    'get_tray_icon',
    'stop_tray_icon',
    'HotkeyWindow',
    'get_hotkey_window',
    'TemplateWindow',
    'get_template_window'
]
