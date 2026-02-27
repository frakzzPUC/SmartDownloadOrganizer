from __future__ import annotations



# Color Palette 
class Colors:
    """Application color tokens."""

    # Backgrounds
    BG_ROOT      = "#0d0d0d"   # Deepest background (window)
    BG_SIDEBAR   = "#111111"   # Sidebar panel
    BG_MAIN      = "#141414"   # Main content area
    BG_CARD      = "#1a1a1a"   # Cards / elevated surfaces
    BG_CARD_ALT  = "#1f1f1f"   # Slightly lighter card variant
    BG_INPUT     = "#1e1e1e"   # Input fields
    BG_HOVER     = "#252525"   # Hover state for list items
    BG_SURFACE   = "#222222"   # Scrollable frames, containers

    # Borders
    BORDER       = "#2a2a2a"   # Subtle default border
    BORDER_LIGHT = "#333333"   # Slightly more visible border
    BORDER_FOCUS = "#4a6fa5"   # Focused input border

    # Text
    TEXT_PRIMARY   = "#e8e8e8" # Main text
    TEXT_SECONDARY = "#999999" # Subtitles, descriptions
    TEXT_MUTED     = "#666666" # Least important text
    TEXT_ACCENT    = "#c0c0c0" # Slightly highlighted

    # Accent / Brand Colors (muted, not neon)
    ACCENT_BLUE    = "#4a6fa5"
    ACCENT_GREEN   = "#3d8b6e"
    ACCENT_PURPLE  = "#7c5cbf"
    ACCENT_AMBER   = "#b8860b"
    ACCENT_RED     = "#a83232"
    ACCENT_CYAN    = "#4a8fa5"

    # Accent hover variants
    ACCENT_BLUE_HOVER   = "#5a82b8"
    ACCENT_GREEN_HOVER  = "#4da080"
    ACCENT_PURPLE_HOVER = "#8d6fd0"
    ACCENT_RED_HOVER    = "#c04040"

    # Semantic Status
    STATUS_SUCCESS = "#3d8b6e"
    STATUS_ERROR   = "#a83232"
    STATUS_WARNING = "#b8860b"
    STATUS_INFO    = "#4a6fa5"

    # Sidebar nav
    NAV_ACTIVE_BG  = "#1e2a3a"   # Active nav item background
    NAV_ACTIVE_FG  = "#7aabdf"   # Active nav item text
    NAV_HOVER_BG   = "#1a1a1a"


# Typography

class Fonts:
    """Font family and size tokens."""
    FAMILY_UI    = "Segoe UI"
    FAMILY_MONO  = "Cascadia Code"
    FALLBACK_MONO = "Consolas"

    SIZE_XS   = 10
    SIZE_SM   = 11
    SIZE_BASE = 13
    SIZE_MD   = 14
    SIZE_LG   = 16
    SIZE_XL   = 20
    SIZE_2XL  = 26
    SIZE_3XL  = 34


# Spacing / Layout

class Spacing:
    """Consistent spacing tokens (pixels)."""
    XS  = 4
    SM  = 8
    MD  = 12
    LG  = 16
    XL  = 20
    XXL = 28
    SIDEBAR_WIDTH = 220
    CARD_RADIUS   = 10
    BTN_RADIUS    = 8
    INPUT_HEIGHT  = 36


# Navigation items definition

NAV_ITEMS = [
    {"id": "dashboard",  "icon": "📊", "label": "Dashboard"},
    {"id": "activity",   "icon": "📋", "label": "Activity"},
    {"id": "rules",      "icon": "⚡", "label": "Rules"},
    {"id": "settings",   "icon": "⚙️", "label": "Settings"},
]
