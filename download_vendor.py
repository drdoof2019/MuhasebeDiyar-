"""
Download Bootstrap and Bootstrap Icons assets for offline use.
Run this script on a machine with internet, then copy static/vendor/ to the offline machine.
"""
import os
import urllib.request
import zipfile
import io
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(BASE_DIR, 'static', 'vendor')

BOOTSTRAP_VERSION = '5.3.3'
BOOTSTRAP_ICONS_VERSION = '1.11.3'

FILES = {
    # Bootstrap CSS
    f'https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css':
        'bootstrap/css/bootstrap.min.css',
    f'https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css.map':
        'bootstrap/css/bootstrap.min.css.map',
    # Bootstrap JS
    f'https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js':
        'bootstrap/js/bootstrap.bundle.min.js',
    f'https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js.map':
        'bootstrap/js/bootstrap.bundle.min.js.map',
    # Bootstrap Icons CSS
    f'https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}/font/bootstrap-icons.css':
        'bootstrap-icons/bootstrap-icons.css',
    f'https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}/font/bootstrap-icons.css.map':
        'bootstrap-icons/bootstrap-icons.css.map',
    # Bootstrap Icons Fonts
    f'https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}/font/fonts/bootstrap-icons.woff':
        'bootstrap-icons/fonts/bootstrap-icons.woff',
    f'https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}/font/fonts/bootstrap-icons.woff2':
        'bootstrap-icons/fonts/bootstrap-icons.woff2',
}


def download_file(url, rel_path):
    """Download a single file to its vendor location."""
    dest = os.path.join(VENDOR_DIR, rel_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    print(f"  Downloading {url}")
    print(f"         -> {rel_path}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
        with open(dest, 'wb') as f:
            f.write(data)
        print(f"         OK ({len(data):,} bytes)")
    except Exception as e:
        print(f"         FAILED: {e}")
        return False
    return True


def main():
    print("=" * 60)
    print("  VENDOR ASSET DOWNLOADER")
    print(f"  Bootstrap {BOOTSTRAP_VERSION} + Icons {BOOTSTRAP_ICONS_VERSION}")
    print("=" * 60)
    print(f"  Target: {VENDOR_DIR}")
    print()
    
    success = 0
    failed = 0
    
    for url, path in FILES.items():
        if download_file(url, path):
            success += 1
        else:
            failed += 1
    
    print()
    print(f"Done: {success} downloaded, {failed} failed.")
    
    if failed > 0:
        print("Some files failed. Check your internet connection and try again.")
        print("You may need to manually download the missing files.")
    else:
        print("All vendor assets ready for offline use!")
        print(f"Files are in: {VENDOR_DIR}")


if __name__ == '__main__':
    main()
