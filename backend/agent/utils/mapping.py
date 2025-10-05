# Shared utilities for toolkits

APP_NAME_MAPPING = {
    # Browsers
    'chrome': 'Google Chrome',
    'google chrome': 'Google Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'arc': 'Arc',
    'brave': 'Brave Browser',
    'edge': 'Microsoft Edge',
    'opera': 'Opera',
    
    # Common apps
    'vscode': 'Visual Studio Code',
    'vs code': 'Visual Studio Code',
    'code': 'Visual Studio Code',
    'notion': 'Notion',
    'slack': 'Slack',
    'discord': 'Discord',
    'spotify': 'Spotify',
    'notes': 'Notes',
    'calendar': 'Calendar',
    'mail': 'Mail',
    'messages': 'Messages',
    'facetime': 'FaceTime',
    'calculator': 'Calculator',
    'terminal': 'Terminal',
    'iterm': 'iTerm',
    'iterm2': 'iTerm',
    'finder': 'Finder',
    'music': 'Music',
    'photos': 'Photos',
    'preview': 'Preview',
    'textedit': 'TextEdit',
    'pages': 'Pages',
    'keynote': 'Keynote',
    'numbers': 'Numbers',
    'zoom': 'zoom.us',
    'obs': 'OBS',
    'vlc': 'VLC',
    'photoshop': 'Adobe Photoshop 2024',
    'illustrator': 'Adobe Illustrator 2024',
}

def normalize_app_name(app_name: str) -> str:
    """
    Normalizes application names to their actual macOS names.
    
    Args:
        app_name: User-provided app name (e.g., 'chrome', 'Chrome')
    
    Returns:
        Actual macOS application name (e.g., 'Google Chrome')
    """
    app_lower = app_name.lower().strip()
    if app_lower in APP_NAME_MAPPING:
        return APP_NAME_MAPPING[app_lower]
    return app_name.title()