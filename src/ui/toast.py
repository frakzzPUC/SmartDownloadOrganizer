from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import Colors, Fonts, Spacing


_TOAST_COLORS = {
    "success": (Colors.STATUS_SUCCESS, "#e8f5e9"),
    "error":   (Colors.STATUS_ERROR,   "#fdecea"),
    "warning": (Colors.STATUS_WARNING, "#fff8e1"),
    "info":    (Colors.STATUS_INFO,    "#e3f2fd"),
}

_TOAST_ICONS = {
    "success": "✓",
    "error":   "✕",
    "warning": "⚠",
    "info":    "ℹ",
}


class ToastNotification(ctk.CTkFrame):
    """
    A floating toast that auto-dismisses after a timeout.

    Usage:
        ToastNotification.show(parent, "File moved!", "success")
    """

    _active_toasts: list[ToastNotification] = []

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        message: str,
        toast_type: str = "info",
        duration_ms: int = 3500,
    ) -> None:
        accent, _ = _TOAST_COLORS.get(toast_type, _TOAST_COLORS["info"])
        icon = _TOAST_ICONS.get(toast_type, "ℹ")

        super().__init__(
            master,
            fg_color=Colors.BG_CARD,
            border_color=accent,
            border_width=1,
            corner_radius=Spacing.CARD_RADIUS,
        )

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

        # Icon badge
        badge = ctk.CTkLabel(
            content,
            text=icon,
            width=28,
            height=28,
            corner_radius=14,
            fg_color=accent,
            text_color="#ffffff",
            font=ctk.CTkFont(size=Fonts.SIZE_BASE, weight="bold"),
        )
        badge.pack(side="left", padx=(0, Spacing.SM))

        # Message
        label = ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
            wraplength=280,
        )
        label.pack(side="left", fill="x", expand=True)

        # Close button
        close_btn = ctk.CTkLabel(
            content,
            text="✕",
            width=20,
            text_color=Colors.TEXT_MUTED,
            font=ctk.CTkFont(size=Fonts.SIZE_XS),
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=(Spacing.SM, 0))
        close_btn.bind("<Button-1>", lambda e: self._dismiss())

        self._duration = duration_ms

    def _show_animated(self, x: int, y: int) -> None:
        """Place the toast and schedule auto-dismiss."""
        self.place(x=x, y=y, anchor="ne")
        self.lift()
        self.after(self._duration, self._dismiss)

    def _dismiss(self) -> None:
        """Remove the toast from display."""
        if self in ToastNotification._active_toasts:
            ToastNotification._active_toasts.remove(self)
        try:
            self.place_forget()
            self.destroy()
        except Exception:
            pass

    @classmethod
    def show(
        cls,
        master: ctk.CTkBaseClass,
        message: str,
        toast_type: str = "info",
        duration_ms: int = 3500,
    ) -> ToastNotification:
        """
        Create and display a toast notification.

        Args:
            master: Parent widget (usually the root App window).
            message: Text to display.
            toast_type: One of 'success', 'error', 'warning', 'info'.
            duration_ms: Auto-dismiss time in milliseconds.
        """
        toast = cls(master, message, toast_type, duration_ms)
        cls._active_toasts.append(toast)

        # Stack toasts vertically from top-right
        try:
            parent_w = master.winfo_width()
        except Exception:
            parent_w = 900

        y_offset = Spacing.LG
        for t in cls._active_toasts[:-1]:
            try:
                y_offset += t.winfo_reqheight() + Spacing.SM
            except Exception:
                y_offset += 50

        toast._show_animated(parent_w - Spacing.LG, y_offset)
        return toast
