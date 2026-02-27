from pathlib import Path

# Application Metadata
APP_NAME = "Smart Download Organizer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "SmartDownloadOrganizer"
DATABASE_NAME = "organizer_history.db"

# Default Paths
DEFAULT_DOWNLOADS_PATH = Path.home() / "Downloads"
DEFAULT_CONFIG_PATH = Path.home() / ".smart_download_organizer"

# File Categories & Extension Mapping
FILE_CATEGORIES: dict[str, list[str]] = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
        ".ico", ".tiff", ".tif", ".raw", ".heic", ".heif",
    ],
    "Documents": [
        ".pdf", ".doc", ".docx", ".odt", ".rtf", ".tex", ".txt",
        ".wpd", ".pages",
    ],
    "Spreadsheets": [
        ".xls", ".xlsx", ".csv", ".ods", ".numbers",
    ],
    "Presentations": [
        ".ppt", ".pptx", ".odp", ".key",
    ],
    "Videos": [
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
        ".m4v", ".mpg", ".mpeg", ".3gp",
    ],
    "Music": [
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
        ".opus", ".aiff",
    ],
    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        ".tar.gz", ".tar.bz2", ".tar.xz",
    ],
    "Executables": [
        ".exe", ".msi", ".bat", ".cmd", ".sh", ".app", ".dmg",
        ".deb", ".rpm", ".apk",
    ],
    "Code": [
        ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".rb", ".go", ".rs", ".php", ".swift", ".kt",
        ".scala", ".r", ".m", ".html", ".css", ".scss", ".sass",
        ".less", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini",
        ".sql", ".sh", ".bash", ".ps1", ".lua", ".dart", ".vue",
        ".jsx", ".tsx",
    ],
    "Fonts": [
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ],
    "Ebooks": [
        ".epub", ".mobi", ".azw", ".azw3", ".fb2", ".djvu",
    ],
    "Torrents": [
        ".torrent",
    ],
    "Disk Images": [
        ".iso", ".img", ".vhd", ".vmdk",
    ],
    "Design": [
        ".psd", ".ai", ".sketch", ".fig", ".xd", ".indd",
    ],
    "3D Models": [
        ".obj", ".stl", ".fbx", ".blend", ".3ds", ".dae",
    ],
    "Data": [
        ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".parquet",
        ".feather", ".hdf5", ".h5",
    ],
}

# Build reverse lookup: extension → category
EXTENSION_TO_CATEGORY: dict[str, str] = {}
for category, extensions in FILE_CATEGORIES.items():
    for ext in extensions:
        EXTENSION_TO_CATEGORY[ext.lower()] = category

# Category used when no match is found
UNCATEGORIZED_FOLDER = "Others"

# File Monitoring Settings
# Seconds to wait before processing a new file (ensures download is complete)
FILE_STABILITY_DELAY = 2.0
# How many times to check file size stability
FILE_STABILITY_CHECKS = 3
# Interval between stability checks (seconds)
FILE_STABILITY_INTERVAL = 1.0

# Minimum file size to process (skip 0-byte temp files)
MIN_FILE_SIZE_BYTES = 1

# File extensions typically used for incomplete downloads
TEMP_EXTENSIONS = {
    ".crdownload",  # Chrome
    ".part",        # Firefox
    ".tmp",         # Generic temp
    ".download",    # Safari
    ".partial",     # IE/Edge
    ".opdownload",  # Opera
}

# UI Constants
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 650
LOG_MAX_ENTRIES = 500

# Status Icons (emoji)
STATUS_MOVED = "✅"
STATUS_ERROR = "❌"
STATUS_DUPLICATE = "⚠️"
STATUS_SKIPPED = "⏭️"
STATUS_MONITORING = "👁️"
STATUS_STOPPED = "⏹️"
