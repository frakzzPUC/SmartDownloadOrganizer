from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from src.models.file_record import FileRecord, FileStatus
from src.ui.theme import Colors, Fonts, Spacing
from src.utils.constants import LOG_MAX_ENTRIES


# Per-status visual config
_LOG_STYLE: dict[str, dict] = {
    FileStatus.MOVED.value: {
        "icon": "✓", "color": Colors.STATUS_SUCCESS, "label": "Moved",
    },
    FileStatus.ERROR.value: {
        "icon": "✕", "color": Colors.STATUS_ERROR, "label": "Error",
    },
    FileStatus.DUPLICATE.value: {
        "icon": "◈", "color": Colors.STATUS_WARNING, "label": "Duplicate",
    },
    FileStatus.SKIPPED.value: {
        "icon": "⏭", "color": Colors.TEXT_MUTED, "label": "Skipped",
    },
}

_SYSTEM_STYLE = {"icon": "●", "color": Colors.STATUS_INFO, "label": "System"}


class LogViewer(ctk.CTkFrame):
    """Modern timeline-style activity log."""

    def __init__(self, master: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._entry_count = 0

        # Header row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))

        ctk.CTkLabel(
            header_row,
            text="Activity",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_LG, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(side="left")

        self._count_badge = ctk.CTkLabel(
            header_row,
            text="0 events",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        )
        self._count_badge.pack(side="left", padx=(Spacing.SM, 0))

        clear_btn = ctk.CTkButton(
            header_row,
            text="Clear",
            width=70,
            height=28,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.BG_CARD,
            hover_color=Colors.BG_HOVER,
            border_color=Colors.BORDER,
            border_width=1,
            text_color=Colors.TEXT_SECONDARY,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            command=self.clear,
        )
        clear_btn.pack(side="right")

        # Scrollable log area
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CARD_RADIUS,
            border_color=Colors.BORDER,
            border_width=1,
        )
        self._scroll.pack(
            fill="both", expand=True,
            padx=Spacing.LG, pady=(0, Spacing.LG),
        )

        # Empty state
        self._empty_label = ctk.CTkLabel(
            self._scroll,
            text="No activity yet.\nStart monitoring to see files being organized.",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_BASE),
            text_color=Colors.TEXT_MUTED,
            justify="center",
        )
        self._empty_label.pack(pady=60)

    # Public API

    def add_entry(self, record: FileRecord) -> None:
        """Add a styled log entry for a file record."""
        style = _LOG_STYLE.get(record.status, _SYSTEM_STYLE)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if record.status == FileStatus.MOVED.value:
            primary = record.original_name
            secondary = (
                f"→  {record.category} / {record.destination_path_obj.name}"
                f"   ·   {record.size_display}"
            )
        elif record.status == FileStatus.DUPLICATE.value:
            primary = f"Duplicate: {record.original_name}"
            secondary = "Matches a previously organized file"
        elif record.status == FileStatus.ERROR.value:
            primary = record.original_name
            secondary = "Could not be organized — check permissions"
        else:
            primary = record.original_name
            secondary = record.status

        self._add_row(style, timestamp, primary, secondary)

    def add_system_message(self, message: str) -> None:
        """Add a system-level informational message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._add_row(_SYSTEM_STYLE, timestamp, message, "")

    def clear(self) -> None:
        """Remove all log entries and show empty state."""
        for w in self._scroll.winfo_children():
            w.destroy()
        self._entry_count = 0
        self._count_badge.configure(text="0 events")
        self._empty_label = ctk.CTkLabel(
            self._scroll,
            text="No activity yet.\nStart monitoring to see files being organized.",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_BASE),
            text_color=Colors.TEXT_MUTED,
            justify="center",
        )
        self._empty_label.pack(pady=60)

    # Internal

    def _add_row(
        self,
        style: dict,
        timestamp: str,
        primary: str,
        secondary: str,
    ) -> None:
        """Build a single log row widget."""
        # Remove empty-state placeholder on first entry
        if self._entry_count == 0:
            try:
                if self._empty_label.winfo_exists():
                    self._empty_label.destroy()
            except Exception:
                pass

        self._entry_count += 1

        # Trim old entries
        children = self._scroll.winfo_children()
        if len(children) > LOG_MAX_ENTRIES:
            children[0].destroy()
            self._entry_count = len(self._scroll.winfo_children()) + 1

        self._count_badge.configure(text=f"{self._entry_count} events")

        # Row container
        row = ctk.CTkFrame(self._scroll, fg_color="transparent", height=44)
        row.pack(fill="x", pady=(0, 1))

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=Spacing.MD, pady=Spacing.XS)

        # Status badge (round dot with icon)
        badge = ctk.CTkLabel(
            inner,
            text=style["icon"],
            width=26,
            height=26,
            corner_radius=13,
            fg_color=style["color"],
            text_color="#ffffff",
            font=ctk.CTkFont(size=Fonts.SIZE_XS, weight="bold"),
        )
        badge.pack(side="left", padx=(0, Spacing.SM))

        # Text column
        text_col = ctk.CTkFrame(inner, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            text_col,
            text=primary,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x")

        if secondary:
            ctk.CTkLabel(
                text_col,
                text=secondary,
                font=ctk.CTkFont(family=Fonts.FAMILY_MONO, size=Fonts.SIZE_XS),
                text_color=Colors.TEXT_MUTED,
                anchor="w",
            ).pack(fill="x")

        # Timestamp (right-aligned)
        ctk.CTkLabel(
            inner,
            text=timestamp,
            font=ctk.CTkFont(family=Fonts.FAMILY_MONO, size=Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED,
            width=60,
        ).pack(side="right")

        # Subtle separator
        ctk.CTkFrame(
            row, height=1, fg_color=Colors.BORDER, corner_radius=0,
        ).pack(fill="x", padx=Spacing.MD)

        # Auto-scroll to bottom
        try:
            self._scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass
