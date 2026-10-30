import os
import sys
import subprocess
import webbrowser

def open_url(url: str):
    """
    跨平台自动打开网页/二维码链接：
    - Windows: start 或 rundll32
    - macOS: open
    - Linux: xdg-open
    """
    try:
        webbrowser.open(url)
    except Exception:
        if sys.platform == "darwin":
            subprocess.run(["open", url], check=False)
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", url], check=False)
        elif sys.platform == "win32":
            os.system(f'start "" "{url}"')

def clear_screen():
    """跨平台清屏"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def get_platform_name():
    if sys.platform == "darwin":
        return "macOS"
    elif sys.platform == "win32":
        return "Windows"
    elif sys.platform.startswith("linux"):
        return "Linux"
    return sys.platform
