import os

# ...existing code...

INSTALLED_APPS = [
    # ...existing apps...
    'apps.downloads',
]

# Download paths
EPG_DOWNLOAD_PATH = os.path.join(MEDIA_ROOT, 'downloaded_epg')
M3U_DOWNLOAD_PATH = os.path.join(MEDIA_ROOT, 'downloaded_m3u')
CUSTOM_DOWNLOAD_PATH = os.path.join(MEDIA_ROOT, 'downloaded_custom')

# ...existing code...