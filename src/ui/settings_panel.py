from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

import customtkinter as ctk

from src.ui.theme import Colors, Fonts, Spacing
from src.utils.config import AppConfig, ConfigManager


class SettingsPanel(ctk.CTkFrame):
    """Premium settings panel for application configuration."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        config: AppConfig,
        config_manager: ConfigManager,
        on_settings_changed: Callable[[], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._config = config
        self._config_manager = config_manager
        self._on_settings_changed = on_settings_changed

        # Header
        ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_LG, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.XS))

        ctk.CTkLabel(
            self,
            text="Configure how Smart Download Organizer works.",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        # scrollable body
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        # Folders Card
        folders_card = self._make_card(body)

        self._section_header(folders_card, "📂", "Folders")

        self._folder_label(folders_card, "Watch Folder")
        watch_row = ctk.CTkFrame(folders_card, fg_color="transparent")
        watch_row.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        watch_row.columnconfigure(0, weight=1)

        self._watch_entry = ctk.CTkEntry(
            watch_row, height=Spacing.INPUT_HEIGHT,
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY, corner_radius=Spacing.BTN_RADIUS,
        )
        self._watch_entry.insert(0, config.watch_folder)
        self._watch_entry.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            watch_row, text="Browse", width=80, height=Spacing.INPUT_HEIGHT,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.BG_HOVER, hover_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_SECONDARY,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            command=self._browse_watch,
        ).grid(row=0, column=1, padx=(Spacing.SM, 0))

        self._folder_label(folders_card, "Destination Folder")
        dest_row = ctk.CTkFrame(folders_card, fg_color="transparent")
        dest_row.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))
        dest_row.columnconfigure(0, weight=1)

        self._dest_entry = ctk.CTkEntry(
            dest_row, height=Spacing.INPUT_HEIGHT,
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY, corner_radius=Spacing.BTN_RADIUS,
        )
        self._dest_entry.insert(0, config.destination_folder)
        self._dest_entry.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            dest_row, text="Browse", width=80, height=Spacing.INPUT_HEIGHT,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.BG_HOVER, hover_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_SECONDARY,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            command=self._browse_dest,
        ).grid(row=0, column=1, padx=(Spacing.SM, 0))

        # Preferences Card
        prefs_card = self._make_card(body)

        self._section_header(prefs_card, "⚙️", "Preferences")

        self._auto_start_var = ctk.BooleanVar(value=config.auto_start_monitoring)
        self._pref_toggle(prefs_card, "Start monitoring on launch",
                          "Begin organizing files as soon as the app opens.",
                          self._auto_start_var)

        self._notifications_var = ctk.BooleanVar(value=config.show_notifications)
        self._pref_toggle(prefs_card, "Show notifications",
                          "Toast notifications for each organized file.",
                          self._notifications_var)

        # Appearance Card
        theme_card = self._make_card(body)

        self._section_header(theme_card, "🎨", "Appearance")

        theme_inner = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_inner.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        ctk.CTkLabel(
            theme_inner, text="Theme",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(side="left")

        self._theme_var = ctk.StringVar(value=config.theme)
        ctk.CTkOptionMenu(
            theme_inner,
            values=["dark", "light", "system"],
            variable=self._theme_var,
            width=140, height=Spacing.INPUT_HEIGHT,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.BG_INPUT,
            button_color=Colors.BORDER_LIGHT,
            button_hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            command=self._on_theme_change,
        ).pack(side="right")

        # Save Button
        ctk.CTkButton(
            body,
            text="Save Settings",
            height=42,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_BASE, weight="bold"),
            command=self._save,
        ).pack(pady=(Spacing.SM, 0))

    # Reusable builders

    def _make_card(self, parent) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent, fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CARD_RADIUS,
            border_color=Colors.BORDER, border_width=1,
        )
        card.pack(fill="x", pady=(0, Spacing.MD))
        return card

    def _section_header(self, parent, icon: str, title: str) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(
            row, text=f"{icon}  {title}",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_MD, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")

    def _folder_label(self, parent, text: str) -> None:
        ctk.CTkLabel(
            parent, text=text, anchor="w",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
        ).pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.XS))

    def _pref_toggle(self, parent, title: str, desc: str, var: ctk.BooleanVar) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info_frame, text=title,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            info_frame, text=desc,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=11),
            text_color=Colors.TEXT_MUTED, anchor="w",
        ).pack(fill="x")
        ctk.CTkSwitch(
            row, text="", variable=var, width=44,
            progress_color=Colors.ACCENT_BLUE,
            button_color=Colors.TEXT_MUTED,
            button_hover_color=Colors.TEXT_SECONDARY,
        ).pack(side="right", padx=(Spacing.MD, 0))

    # Actions

    def _browse_watch(self) -> None:
        folder = filedialog.askdirectory(
            title="Select Watch Folder",
            initialdir=self._watch_entry.get(),
        )
        if folder:
            self._watch_entry.delete(0, "end")
            self._watch_entry.insert(0, folder)

    def _browse_dest(self) -> None:
        folder = filedialog.askdirectory(
            title="Select Destination Folder",
            initialdir=self._dest_entry.get(),
        )
        if folder:
            self._dest_entry.delete(0, "end")
            self._dest_entry.insert(0, folder)

    def _on_theme_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)

    def _save(self) -> None:
        watch = self._watch_entry.get().strip()
        dest = self._dest_entry.get().strip()

        if not Path(watch).exists():
            messagebox.showerror(
                "Invalid Path", f"Watch folder does not exist:\n{watch}"
            )
            return

        if not Path(dest).exists():
            try:
                Path(dest).mkdir(parents=True, exist_ok=True)
            except OSError:
                messagebox.showerror(
                    "Invalid Path",
                    f"Cannot create destination folder:\n{dest}",
                )
                return

        self._config.watch_folder = watch
        self._config.destination_folder = dest
        self._config.auto_start_monitoring = self._auto_start_var.get()
        self._config.show_notifications = self._notifications_var.get()
        self._config.theme = self._theme_var.get()

        self._config_manager.save(self._config)
        messagebox.showinfo("Settings", "Settings saved successfully!")

        if self._on_settings_changed:
            self._on_settings_changed()
