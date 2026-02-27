from __future__ import annotations

import queue
import threading

import customtkinter as ctk

from src.models.database import Database
from src.models.file_record import FileRecord
from src.services.file_organizer import FileOrganizer
from src.services.file_monitor import FileMonitor
from src.ui.dashboard import Dashboard
from src.ui.log_viewer import LogViewer
from src.ui.rules_editor import RulesEditor
from src.ui.settings_panel import SettingsPanel
from src.ui.theme import Colors, Fonts, Spacing, NAV_ITEMS
from src.ui.toast import ToastNotification
from src.utils.config import AppConfig, ConfigManager
from src.utils.constants import (
    WINDOW_TITLE,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from src.utils.logger import logger

# Event types for the UI queue
_EVENT_FILE_RECORD = "file_record"
_EVENT_SYSTEM_MSG = "system_message"
_EVENT_REFRESH_DASHBOARD = "refresh_dashboard"


class App(ctk.CTk):
    """Main application window with sidebar navigation."""

    def __init__(self) -> None:
        super().__init__()

        # Thread-safe event queue
        self._ui_queue: queue.Queue[tuple[str, object]] = queue.Queue()

        # Configuration
        self._config_manager = ConfigManager()
        self._config = self._config_manager.load()

        # Apply theme
        ctk.set_appearance_mode(self._config.theme)
        ctk.set_default_color_theme("blue")

        # Window setup
        self.title(WINDOW_TITLE)
        self.configure(fg_color=Colors.BG_ROOT)
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Core services
        self._db = Database()
        self._organizer = FileOrganizer(
            config=self._config,
            database=self._db,
            on_file_organized=self._on_file_organized,
        )
        self._monitor = FileMonitor(
            organizer=self._organizer,
            watch_path=self._config.watch_path,
        )

        # Track the active page
        self._active_page: str = "dashboard"
        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        # Build UI
        self._build_ui()

        # Start the UI event-queue poller
        self._poll_ui_queue()

        # Auto-start if configured
        if self._config.auto_start_monitoring:
            self.after(500, self._toggle_monitoring)

        logger.info("Application started")

    # Layout
 

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #  Sidebar 
        self._sidebar = ctk.CTkFrame(
            self,
            width=Spacing.SIDEBAR_WIDTH,
            fg_color=Colors.BG_SIDEBAR,
            corner_radius=0,
        )
        self._sidebar.grid(row=0, column=0, sticky="ns")
        self._sidebar.grid_propagate(False)

        self._build_sidebar()

        # Main container 
        self._main = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._main.grid(row=0, column=1, sticky="nsew")
        self._main.grid_rowconfigure(1, weight=1)
        self._main.grid_columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_pages()

        # ── Show default page 
        self._show_page("dashboard")
        self._refresh_dashboard()

    # Sidebar 

    def _build_sidebar(self) -> None:
        # Brand header
        brand = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=Spacing.LG, pady=(Spacing.XL, Spacing.LG))

        ctk.CTkLabel(
            brand,
            text="SDO",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_XL, weight="bold"),
            text_color=Colors.ACCENT_BLUE,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            brand,
            text="Smart Download\nOrganizer",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
            justify="left",
        ).pack(fill="x")

        # Separator
        ctk.CTkFrame(
            self._sidebar, fg_color=Colors.BORDER, height=1,
        ).pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.SM))

        # Navigation buttons
        for item in NAV_ITEMS:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {item['icon']}   {item['label']}",
                anchor="w",
                height=40,
                corner_radius=Spacing.BTN_RADIUS,
                fg_color="transparent",
                hover_color=Colors.NAV_HOVER_BG,
                text_color=Colors.TEXT_SECONDARY,
                font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_BASE),
                command=lambda pid=item["id"]: self._show_page(pid),
            )
            btn.pack(fill="x", padx=Spacing.SM, pady=1)
            self._nav_buttons[item["id"]] = btn

        # Spacer
        ctk.CTkFrame(self._sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Monitoring toggle at bottom
        self._sidebar_monitor_btn = ctk.CTkButton(
            self._sidebar,
            text="▶  Start Monitoring",
            height=38,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.ACCENT_GREEN,
            hover_color=Colors.ACCENT_GREEN_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM, weight="bold"),
            command=self._toggle_monitoring,
        )
        self._sidebar_monitor_btn.pack(
            fill="x", padx=Spacing.MD, pady=(0, Spacing.SM),
        )

        # Status line
        self._sidebar_status = ctk.CTkLabel(
            self._sidebar,
            text="●  Stopped",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED,
        )
        self._sidebar_status.pack(pady=(0, Spacing.LG))

    #  Top bar 

    def _build_topbar(self) -> None:
        topbar = ctk.CTkFrame(
            self._main, fg_color=Colors.BG_CARD, height=52, corner_radius=0,
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        # Page title (updated when switching pages)
        self._page_title = ctk.CTkLabel(
            topbar,
            text="Dashboard",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_MD, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        )
        self._page_title.grid(row=0, column=0, padx=Spacing.LG, pady=Spacing.MD)

        # Watch path hint
        self._path_label = ctk.CTkLabel(
            topbar,
            text=f"📁  {self._config.watch_folder}",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED,
            anchor="e",
        )
        self._path_label.grid(row=0, column=1, sticky="e", padx=Spacing.MD)

        # Organize existing button
        ctk.CTkButton(
            topbar,
            text="📂  Organize Now",
            width=140,
            height=32,
            corner_radius=Spacing.BTN_RADIUS,
            fg_color=Colors.ACCENT_PURPLE,
            hover_color=Colors.ACCENT_PURPLE_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=Fonts.FAMILY_UI, size=Fonts.SIZE_SM, weight="bold"),
            command=self._organize_existing,
        ).grid(row=0, column=2, padx=(0, Spacing.LG), pady=Spacing.MD)

    #Content pages 
    def _build_pages(self) -> None:
        self._content = ctk.CTkFrame(
            self._main, fg_color=Colors.BG_MAIN, corner_radius=0,
        )
        self._content.grid(row=1, column=0, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        # Create all panels (only one visible at a time)
        self._dashboard = Dashboard(self._content)
        self._log_viewer = LogViewer(self._content)
        self._rules_editor = RulesEditor(
            self._content, rule_engine=self._organizer.rule_engine,
        )
        self._settings_panel = SettingsPanel(
            self._content,
            config=self._config,
            config_manager=self._config_manager,
            on_settings_changed=self._on_settings_changed,
        )

        self._pages: dict[str, ctk.CTkFrame] = {
            "dashboard": self._dashboard,
            "activity": self._log_viewer,
            "rules": self._rules_editor,
            "settings": self._settings_panel,
        }

    def _show_page(self, page_id: str) -> None:
        if page_id == self._active_page:
            return

        # Hide current
        self._pages[self._active_page].grid_forget()

        # Show new
        self._pages[page_id].grid(row=0, column=0, sticky="nsew")
        self._active_page = page_id

        # Update nav button states
        for nid, btn in self._nav_buttons.items():
            if nid == page_id:
                btn.configure(
                    fg_color=Colors.NAV_ACTIVE_BG,
                    text_color=Colors.NAV_ACTIVE_FG,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Colors.TEXT_SECONDARY,
                )

        # Update topbar title
        label_map = {
            "dashboard": "Dashboard",
            "activity": "Activity Log",
            "rules": "Custom Rules",
            "settings": "Settings",
        }
        self._page_title.configure(text=label_map.get(page_id, ""))

        # Refresh dashboard when switching to it
        if page_id == "dashboard":
            self._refresh_dashboard()

    # Control Actions

    def _toggle_monitoring(self) -> None:
        if self._monitor.is_running:
            self._monitor.stop()
            self._sidebar_monitor_btn.configure(
                text="▶  Start Monitoring",
                fg_color=Colors.ACCENT_GREEN,
                hover_color=Colors.ACCENT_GREEN_HOVER,
            )
            self._sidebar_status.configure(
                text="●  Stopped",
                text_color=Colors.TEXT_MUTED,
            )
            self._log_viewer.add_system_message("Monitoring stopped")
        else:
            success = self._monitor.start()
            if success:
                self._sidebar_monitor_btn.configure(
                    text="■  Stop Monitoring",
                    fg_color=Colors.ACCENT_RED,
                    hover_color=Colors.ACCENT_RED_HOVER,
                )
                self._sidebar_status.configure(
                    text="●  Monitoring",
                    text_color=Colors.ACCENT_GREEN,
                )
                self._log_viewer.add_system_message(
                    f"Monitoring started: {self._config.watch_folder}"
                )
            else:
                self._log_viewer.add_system_message(
                    "Failed to start monitoring. Check the watch folder path."
                )

    def _organize_existing(self) -> None:
        self._log_viewer.add_system_message("Organizing existing files...")

        def _worker() -> None:
            results = self._organizer.organize_existing_files()
            self._ui_queue.put((
                _EVENT_SYSTEM_MSG,
                f"Done! Organized {len(results)} file(s).",
            ))
            self._ui_queue.put((_EVENT_REFRESH_DASHBOARD, None))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    # Thread-safe UI Queue

    def _poll_ui_queue(self) -> None:
        """
        Drain the event queue and apply updates on the main thread.
        Runs every 150 ms via after(), guaranteeing all UI mutations
        happen on the tkinter main loop.
        """
        try:
            while True:
                event_type, data = self._ui_queue.get_nowait()
                if event_type == _EVENT_FILE_RECORD:
                    record: FileRecord = data  # type: ignore[assignment]
                    self._log_viewer.add_entry(record)
                    self._refresh_dashboard()
                    # Toast notification for file moves
                    if self._config.show_notifications:
                        ToastNotification.show(
                            self,
                            f"{record.original_name} → {record.category}",
                            toast_type="success",
                        )
                elif event_type == _EVENT_SYSTEM_MSG:
                    self._log_viewer.add_system_message(str(data))
                elif event_type == _EVENT_REFRESH_DASHBOARD:
                    self._refresh_dashboard()
        except queue.Empty:
            pass
        finally:
            self.after(150, self._poll_ui_queue)

    # Callbacks

    def _on_file_organized(self, record: FileRecord) -> None:
        """Called from background thread — enqueue only."""
        self._ui_queue.put((_EVENT_FILE_RECORD, record))

    def _on_settings_changed(self) -> None:
        self._monitor.watch_path = self._config.watch_path
        self._path_label.configure(text=f"📁  {self._config.watch_folder}")
        self._log_viewer.add_system_message("Settings updated")

    def _refresh_dashboard(self) -> None:
        stats = self._db.get_statistics()
        self._dashboard.update_stats(stats)

    def _on_close(self) -> None:
        logger.info("Application closing...")
        if self._monitor.is_running:
            self._monitor.stop()
        self._db.close()
        self.destroy()
        self.destroy()
