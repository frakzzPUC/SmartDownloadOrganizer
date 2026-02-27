from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from src.utils.constants import FILE_STABILITY_DELAY
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.services.file_organizer import FileOrganizer


class _DownloadHandler(FileSystemEventHandler):
    """
    Watchdog event handler that processes new files.

    Reacts to file creation and file move events (some browsers
    move temp files to final names instead of creating new ones).
    """

    def __init__(self, organizer: FileOrganizer) -> None:
        super().__init__()
        self._organizer = organizer
        self._processing_lock = threading.Lock()

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        self._schedule_processing(Path(event.src_path))

    def on_moved(self, event: FileMovedEvent) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        self._schedule_processing(Path(event.dest_path))

    def _schedule_processing(self, file_path: Path) -> None:
        """
        Process a file in a separate thread with a slight delay.

        The delay allows the file system to stabilize (e.g., browser
        finishing the write).
        """
        timer = threading.Timer(
            FILE_STABILITY_DELAY,
            self._process_file,
            args=(file_path,),
        )
        timer.daemon = True
        timer.start()

    def _process_file(self, file_path: Path) -> None:
        """Thread-safe file processing."""
        with self._processing_lock:
            try:
                self._organizer.organize_file(file_path)
            except Exception as e:
                logger.error(
                    "Unexpected error processing '%s': %s",
                    file_path.name, e,
                )


class FileMonitor:
    """
    Manages the watchdog Observer lifecycle.

    Provides start/stop control and status reporting for the UI.
    """

    def __init__(self, organizer: FileOrganizer, watch_path: Path) -> None:
        self._organizer = organizer
        self._watch_path = watch_path
        self._observer: Observer | None = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def watch_path(self) -> Path:
        return self._watch_path

    @watch_path.setter
    def watch_path(self, path: Path) -> None:
        was_running = self._is_running
        if was_running:
            self.stop()
        self._watch_path = path
        if was_running:
            self.start()

    def start(self) -> bool:
        """
        Start monitoring the watch folder.

        Returns:
            True if started successfully, False otherwise.
        """
        if self._is_running:
            logger.warning("Monitor is already running")
            return True

        if not self._watch_path.exists():
            logger.error("Watch folder does not exist: %s", self._watch_path)
            return False

        handler = _DownloadHandler(self._organizer)
        self._observer = Observer()
        self._observer.schedule(
            handler,
            str(self._watch_path),
            recursive=False,
        )

        try:
            self._observer.start()
            self._is_running = True
            logger.info("Monitoring started: %s", self._watch_path)
            return True
        except OSError as e:
            logger.error("Failed to start monitor: %s", e)
            self._observer = None
            return False

    def stop(self) -> None:
        """Stop monitoring."""
        if not self._is_running or self._observer is None:
            return

        self._observer.stop()
        self._observer.join(timeout=5)
        self._observer = None
        self._is_running = False
        logger.info("Monitoring stopped")
