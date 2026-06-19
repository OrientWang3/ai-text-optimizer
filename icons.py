"""
图标生成模块 - 使用Pillow绘制简洁图标
"""

from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
from typing import Optional
import io


class IconManager:
    """图标管理器"""

    def __init__(self):
        self._icons = {}
        self._ctk_images = {}

    def create_icon(self, name: str, size: int = 20, color: str = "#cdd6f4", bg_color: str = None) -> ctk.CTkImage:
        """
        创建图标

        Args:
            name: 图标名称
            size: 图标大小
            color: 图标颜色
            bg_color: 背景颜色

        Returns:
            CTkImage对象
        """
        cache_key = f"{name}_{size}_{color}_{bg_color}"
        if cache_key in self._ctk_images:
            return self._ctk_images[cache_key]

        # 创建PIL图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if bg_color:
            draw.rounded_rectangle([0, 0, size-1, size-1], radius=4, fill=bg_color)

        # 根据名称绘制不同图标
        method = getattr(self, f"_draw_{name}", None)
        if method:
            method(draw, size, color)

        # 转换为CTkImage
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        self._ctk_images[cache_key] = ctk_img
        return ctk_img

    def _draw_close(self, draw: ImageDraw, size: int, color: str):
        """关闭图标 X"""
        margin = size // 4
        draw.line([(margin, margin), (size - margin, size - margin)], fill=color, width=2)
        draw.line([(size - margin, margin), (margin, size - margin)], fill=color, width=2)

    def _draw_copy(self, draw: ImageDraw, size: int, color: str):
        """复制图标"""
        # 两个重叠的矩形
        draw.rectangle([4, 6, 12, 16], outline=color, width=1)
        draw.rectangle([8, 2, 16, 12], outline=color, width=1)
        draw.rectangle([8, 2, 16, 12], fill="#1e1e2e", width=1)
        draw.rectangle([8, 2, 16, 12], outline=color, width=1)

    def _draw_save(self, draw: ImageDraw, size: int, color: str):
        """保存图标"""
        # 磁盘形状
        draw.rectangle([3, 2, 17, 18], outline=color, width=1)
        draw.rectangle([6, 2, 14, 8], fill=color)
        draw.rectangle([6, 12, 14, 18], outline=color, width=1)

    def _draw_reset(self, draw: ImageDraw, size: int, color: str):
        """重置图标 - 循环箭头"""
        draw.arc([3, 3, 17, 17], 0, 270, fill=color, width=2)
        # 箭头头部
        draw.polygon([(16, 5), (18, 10), (13, 9)], fill=color)

    def _draw_test(self, draw: ImageDraw, size: int, color: str):
        """测试连接图标 - 链接"""
        draw.arc([2, 6, 10, 14], 180, 0, fill=color, width=2)
        draw.arc([10, 6, 18, 14], 0, 180, fill=color, width=2)
        draw.line([(6, 10), (14, 10)], fill=color, width=2)

    def _draw_settings(self, draw: ImageDraw, size: int, color: str):
        """设置图标 - 齿轮"""
        center = size // 2
        # 内圆
        draw.ellipse([center-3, center-3, center+3, center+3], outline=color, width=1)
        # 外圆
        draw.arc([center-7, center-7, center+7, center+7], 0, 360, fill=color, width=2)
        # 齿轮齿
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            import math
            rad = math.radians(angle)
            x1 = center + int(7 * math.cos(rad))
            y1 = center + int(7 * math.sin(rad))
            x2 = center + int(9 * math.cos(rad))
            y2 = center + int(9 * math.sin(rad))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

    def _draw_error(self, draw: ImageDraw, size: int, color: str):
        """错误图标 - 感叹号"""
        # 圆形
        draw.ellipse([2, 2, size-2, size-2], outline=color, width=2)
        # 感叹号
        center = size // 2
        draw.line([(center, 6), (center, center+2)], fill=color, width=2)
        draw.ellipse([center-1, center+4, center+1, center+6], fill=color)

    def _draw_code(self, draw: ImageDraw, size: int, color: str):
        """代码图标 - 尖括号"""
        draw.line([(6, 6), (2, 10), (6, 14)], fill=color, width=2)
        draw.line([(14, 6), (18, 10), (14, 14)], fill=color, width=2)
        draw.line([(11, 4), (9, 16)], fill=color, width=2)

    def _draw_log(self, draw: ImageDraw, size: int, color: str):
        """日志图标 - 列表"""
        for y in [4, 8, 12, 16]:
            draw.rectangle([2, y, 4, y+2], fill=color)
            draw.line([(7, y+1), (18, y+1)], fill=color, width=1)

    def _draw_config(self, draw: ImageDraw, size: int, color: str):
        """配置图标 - 齿轮+滑块"""
        draw.rectangle([2, 8, 18, 12], outline=color, width=1)
        draw.ellipse([6, 6, 14, 14], outline=color, width=1)
        draw.ellipse([8, 8, 12, 12], fill=color)

    def _draw_text(self, draw: ImageDraw, size: int, color: str):
        """文本图标 - T"""
        draw.line([(6, 4), (14, 4)], fill=color, width=2)
        draw.line([(10, 4), (10, 16)], fill=color, width=2)
        draw.line([(7, 16), (13, 16)], fill=color, width=2)

    def _draw_source(self, draw: ImageDraw, size: int, color: str):
        """来源图标 - 窗口"""
        draw.rectangle([2, 4, 18, 16], outline=color, width=1)
        draw.line([(2, 7), (18, 7)], fill=color, width=1)
        draw.ellipse([4, 9, 6, 11], fill=color)
        draw.ellipse([7, 9, 9, 11], fill=color)

    def _draw_ai(self, draw: ImageDraw, size: int, color: str):
        """AI图标 - 大脑/神经网络"""
        center = size // 2
        # 中心点
        draw.ellipse([center-2, center-2, center+2, center+2], fill=color)
        # 连接线
        for angle in [0, 60, 120, 180, 240, 300]:
            import math
            rad = math.radians(angle)
            x1 = center + int(3 * math.cos(rad))
            y1 = center + int(3 * math.sin(rad))
            x2 = center + int(8 * math.cos(rad))
            y2 = center + int(8 * math.sin(rad))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
            draw.ellipse([x2-2, y2-2, x2+2, y2+2], outline=color, width=1)


# 全局实例
_icon_manager: Optional[IconManager] = None


def get_icon_manager() -> IconManager:
    """获取全局图标管理器"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager
