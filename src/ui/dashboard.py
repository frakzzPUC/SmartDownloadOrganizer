from __future__ import annotations

from typing import Any

import customtkinter as ctk

from src.ui.theme import Colors, Fonts, Spacing
from src.utils.helpers import format_file_size


# Category emoji lookup
_CAT_ICONS: dict[str, str] = {
    "Images": "🖼", "Documents": "📄", "Videos": "🎬", "Music": "🎵",
    "Archives": "📦", "Executables": "⚙", "Code": "💻",
    "Spreadsheets": "📊", "Presentations": "📽", "Fonts": "🔤",
    "Ebooks": "📚", "Torrents": "🌐", "Disk Images": "💿",
    "Design": "🎨", "3D Models": "🧊", "Data": "🗄", "Others": "📁",
}


class StatCard(ctk.CTkFrame):
    """An elegant metric card with icon, value, and label."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: str,
        icon: str = "📊",
        value: str = "0",
        accent: str = Colors.ACCENT_BLUE,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CARD_RADIUS,
            border_color=Colors.BORDER,
            border_width=1,
            **kwargs,
        )

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Top row: icon badge + title
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        badge = ctk.CTkLabel(
            top,
            text=icon,
            width=32, height=32,
            corner_radius=8,
            fg_color=accent,
            text_color="#ffffff",
            font=ctk.CTkFont(size=Fonts.SIZE_BASE),
        )
        badge.pack(side="left")

        ctk.CTkLabel(
            top,
            text=title,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        ).pack(side="left", padx=(Spacing.SM, 0))

        # Value (large)
        self._value_label = ctk.CTkLabel(
            inner,
            text=value,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_3XL, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        )
        self._value_label.pack(fill="x", pady=(Spacing.SM, 0))

    def set_value(self, value: str) -> None:
        self._value_label.configure(text=value)


class Dashboard(ctk.CTkFrame):
    """Premium dashboard with metric cards and category breakdown."""

    def __init__(self, master: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        # Header
        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_LG, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.XS))

        ctk.CTkLabel(
            self,
            text="Overview of your file organization activity",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        #  Stats Cards Grid 
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        cards.columnconfigure((0, 1, 2, 3), weight=1)

        self._card_total = StatCard(
            cards, "Total Organized", icon="📂",
            accent=Colors.ACCENT_BLUE,
        )
        self._card_total.grid(row=0, column=0, padx=(0, Spacing.SM), pady=Spacing.XS, sticky="nsew")

        self._card_today = StatCard(
            cards, "Today", icon="📅",
            accent=Colors.ACCENT_GREEN,
        )
        self._card_today.grid(row=0, column=1, padx=Spacing.SM, pady=Spacing.XS, sticky="nsew")

        self._card_week = StatCard(
            cards, "This Week", icon="📆",
            accent=Colors.ACCENT_PURPLE,
        )
        self._card_week.grid(row=0, column=2, padx=Spacing.SM, pady=Spacing.XS, sticky="nsew")

        self._card_size = StatCard(
            cards, "Total Size", icon="💾",
            accent=Colors.ACCENT_AMBER,
        )
        self._card_size.grid(row=0, column=3, padx=(Spacing.SM, 0), pady=Spacing.XS, sticky="nsew")

        # Category Breakdown
        cat_card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CARD_RADIUS,
            border_color=Colors.BORDER,
            border_width=1,
        )
        cat_card.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        cat_header = ctk.CTkFrame(cat_card, fg_color="transparent")
        cat_header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))

        ctk.CTkLabel(
            cat_header,
            text="Categories",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_MD, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(side="left")

        self._categories_frame = ctk.CTkScrollableFrame(
            cat_card,
            fg_color="transparent",
        )
        self._categories_frame.pack(
            fill="both", expand=True,
            padx=Spacing.MD, pady=(0, Spacing.MD),
        )

    def update_stats(self, stats: dict[str, Any]) -> None:
        """Refresh all dashboard data."""
        self._card_total.set_value(str(stats.get("total_files", 0)))
        self._card_today.set_value(str(stats.get("today_files", 0)))
        self._card_week.set_value(str(stats.get("week_files", 0)))
        self._card_size.set_value(format_file_size(stats.get("total_size", 0)))

        # Rebuild category rows
        for w in self._categories_frame.winfo_children():
            w.destroy()

        categories: dict[str, int] = stats.get("categories", {})
        if not categories:
            ctk.CTkLabel(
                self._categories_frame,
                text="No files organized yet",
                text_color=Colors.TEXT_MUTED,
                font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_BASE),
            ).pack(pady=30)
            return

        max_count = max(categories.values()) if categories else 1
        bar_colors = [
            Colors.ACCENT_BLUE, Colors.ACCENT_GREEN, Colors.ACCENT_PURPLE,
            Colors.ACCENT_AMBER, Colors.ACCENT_CYAN, Colors.ACCENT_RED,
        ]

        for idx, (cat_name, count) in enumerate(categories.items()):
            row = ctk.CTkFrame(self._categories_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            row.columnconfigure(2, weight=1)

            icon = _CAT_ICONS.get(cat_name, "📁")
            ctk.CTkLabel(
                row, text=icon, width=24,
                font=ctk.CTkFont(size=Fonts.SIZE_BASE),
            ).grid(row=0, column=0, padx=(Spacing.SM, Spacing.XS))

            ctk.CTkLabel(
                row, text=cat_name, width=110, anchor="w",
                font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
                text_color=Colors.TEXT_SECONDARY,
            ).grid(row=0, column=1, padx=(0, Spacing.SM))

            bar = ctk.CTkProgressBar(
                row,
                height=8,
                corner_radius=4,
                fg_color=Colors.BG_SURFACE,
                progress_color=bar_colors[idx % len(bar_colors)],
            )
            bar.grid(row=0, column=2, sticky="ew", padx=Spacing.XS)
            bar.set(max(count / max_count, 0.04))

            ctk.CTkLabel(
                row, text=str(count), width=36,
                font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM, weight="bold"),
                text_color=Colors.TEXT_PRIMARY,
            ).grid(row=0, column=3, padx=(Spacing.XS, Spacing.SM))
