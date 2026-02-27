from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from src.models.file_record import CustomRule
from src.services.rule_engine import RuleEngine
from src.ui.theme import Colors, Fonts, Spacing


class RulesEditor(ctk.CTkFrame):
    """Premium panel for managing custom file organization rules."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        rule_engine: RuleEngine,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._rule_engine = rule_engine

        # Header
        ctk.CTkLabel(
            self,
            text="Custom Rules",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_LG, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.XS))

        ctk.CTkLabel(
            self,
            text="Rules are evaluated in priority order. First matching rule wins.",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        # Add Rule Card
        form_card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CARD_RADIUS,
            border_color=Colors.BORDER,
            border_width=1,
        )
        form_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        form_inner.columnconfigure((1, 3, 5), weight=1)

        # Row 1: Name, Pattern, Folder
        self._make_field_label(form_inner, "Name", 0, 0)
        self._name_entry = ctk.CTkEntry(
            form_inner,
            placeholder_text="Rule name",
            height=Spacing.INPUT_HEIGHT,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Spacing.BTN_RADIUS,
        )
        self._name_entry.grid(row=0, column=1, sticky="ew", padx=Spacing.XS, pady=Spacing.XS)

        self._make_field_label(form_inner, "Pattern", 0, 2)
        self._pattern_entry = ctk.CTkEntry(
            form_inner,
            placeholder_text="e.g., invoice",
            height=Spacing.INPUT_HEIGHT,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Spacing.BTN_RADIUS,
        )
        self._pattern_entry.grid(row=0, column=3, sticky="ew", padx=Spacing.XS, pady=Spacing.XS)

        self._make_field_label(form_inner, "Folder", 0, 4)
        self._folder_entry = ctk.CTkEntry(
            form_inner,
            placeholder_text="e.g., Finance",
            height=Spacing.INPUT_HEIGHT,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Spacing.BTN_RADIUS,
        )
        self._folder_entry.grid(row=0, column=5, sticky="ew", padx=Spacing.XS, pady=Spacing.XS)

        # Row 2: Options + Add button
        opts = ctk.CTkFrame(form_inner, fg_color="transparent")
        opts.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(Spacing.SM, 0))

        self._regex_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            opts, text="Regex", variable=self._regex_var,
            width=80, checkbox_height=18, checkbox_width=18,
            border_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_SECONDARY,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
        ).pack(side="left", padx=(0, Spacing.MD))

        self._case_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            opts, text="Case Sensitive", variable=self._case_var,
            width=130, checkbox_height=18, checkbox_width=18,
            border_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_SECONDARY,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
        ).pack(side="left")

        ctk.CTkButton(
            opts,
            text="+ Add Rule",
            width=110,
            height=Spacing.INPUT_HEIGHT,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM, weight="bold"),
            command=self._add_rule,
        ).pack(side="right")

        # Rules List Card
        list_card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CARD_RADIUS,
            border_color=Colors.BORDER,
            border_width=1,
        )
        list_card.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        list_header = ctk.CTkFrame(list_card, fg_color="transparent")
        list_header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(
            list_header,
            text="Active Rules",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_MD, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")

        self._rules_frame = ctk.CTkScrollableFrame(
            list_card, fg_color="transparent",
        )
        self._rules_frame.pack(
            fill="both", expand=True,
            padx=Spacing.MD, pady=(0, Spacing.MD),
        )

        self._refresh_list()

    # Helpers

    @staticmethod
    def _make_field_label(parent, text: str, row: int, col: int) -> None:
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
        ).grid(row=row, column=col, padx=Spacing.XS, pady=Spacing.XS, sticky="w")

    # Actions

    def _add_rule(self) -> None:
        name = self._name_entry.get().strip()
        pattern = self._pattern_entry.get().strip()
        folder = self._folder_entry.get().strip()

        if not pattern or not folder:
            messagebox.showwarning(
                "Incomplete Rule",
                "Please fill in at least the Pattern and Folder fields.",
            )
            return

        if not name:
            name = f"'{pattern}' → {folder}"

        self._rule_engine.add_rule(
            name=name, pattern=pattern, target_folder=folder,
            is_regex=self._regex_var.get(),
            case_sensitive=self._case_var.get(),
        )

        self._name_entry.delete(0, "end")
        self._pattern_entry.delete(0, "end")
        self._folder_entry.delete(0, "end")
        self._regex_var.set(False)
        self._case_var.set(False)
        self._refresh_list()

    def _delete_rule(self, rule_id: int) -> None:
        if messagebox.askyesno("Delete Rule", "Remove this rule?"):
            self._rule_engine.delete_rule(rule_id)
            self._refresh_list()

    def _toggle_rule(self, rule: CustomRule) -> None:
        rule.enabled = not rule.enabled
        self._rule_engine.update_rule(rule)
        self._refresh_list()

    def _refresh_list(self) -> None:
        for w in self._rules_frame.winfo_children():
            w.destroy()

        rules = self._rule_engine.rules

        if not rules:
            ctk.CTkLabel(
                self._rules_frame,
                text="No custom rules yet. Add one above!",
                text_color=Colors.TEXT_MUTED,
                font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_BASE),
            ).pack(pady=30)
            return

        for rule in rules:
            row = ctk.CTkFrame(
                self._rules_frame,
                fg_color=Colors.BG_CARD_ALT,
                corner_radius=Spacing.BTN_RADIUS,
            )
            row.pack(fill="x", pady=2)
            row.columnconfigure(1, weight=1)

            # Toggle button
            icon = "●" if rule.enabled else "○"
            icon_color = Colors.ACCENT_GREEN if rule.enabled else Colors.TEXT_MUTED
            toggle_btn = ctk.CTkButton(
                row, text=icon, width=32, height=32,
                corner_radius=16,
                fg_color="transparent",
                hover_color=Colors.BG_HOVER,
                text_color=icon_color,
                font=ctk.CTkFont(size=Fonts.SIZE_BASE),
                command=lambda r=rule: self._toggle_rule(r),
            )
            toggle_btn.grid(row=0, column=0, padx=(Spacing.SM, 0), pady=Spacing.XS)

            # Rule info
            regex_tag = "  [regex]" if rule.is_regex else ""
            info_text = f"{rule.name}   ·   '{rule.pattern}'{regex_tag}  →  {rule.target_folder}"
            ctk.CTkLabel(
                row, text=info_text, anchor="w",
                font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
                text_color=Colors.TEXT_PRIMARY if rule.enabled else Colors.TEXT_MUTED,
            ).grid(row=0, column=1, sticky="ew", padx=Spacing.SM, pady=Spacing.SM)

            # Delete button
            ctk.CTkButton(
                row, text="✕", width=32, height=32,
                corner_radius=16,
                fg_color="transparent",
                hover_color=Colors.ACCENT_RED,
                text_color=Colors.TEXT_MUTED,
                font=ctk.CTkFont(size=Fonts.SIZE_SM, weight="bold"),
                command=lambda rid=rule.id: self._delete_rule(rid),
            ).grid(row=0, column=2, padx=(0, Spacing.SM), pady=Spacing.XS)
